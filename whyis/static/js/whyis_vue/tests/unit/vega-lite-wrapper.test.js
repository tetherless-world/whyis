/**
 * Unit tests for VegaLiteWrapper component
 * Tests the core visualization component that wraps Vega-Lite charts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { shallowMountComponent, flushPromises } from '../helpers/test-utils.js';
import VegaLiteWrapper from '../../components/vega-lite-wrapper.vue';

// Mock vega-embed since we can't render actual charts in tests
vi.mock('vega-embed', () => ({
  default: vi.fn(() => Promise.resolve({
    view: {
      insert: vi.fn().mockReturnThis(),
      resize: vi.fn().mockReturnThis(),
      run: vi.fn().mockReturnThis()
    }
  }))
}));

// Mock vega-lite schema to avoid URL resolution issues
vi.mock('vega-lite/build/vega-lite-schema.json', () => ({
  default: {
    type: 'object',
    properties: {
      mark: { type: 'string' },
      encoding: { type: 'object' }
    }
  }
}));

// Mock the debounce utility
vi.mock('../../utilities/debounce', () => ({
  default: vi.fn((fn) => fn) // Return function immediately for testing
}));

describe('VegaLiteWrapper Component', () => {
  let consoleWarnSpy;
  let consoleDebugSpy;

  beforeEach(() => {
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    consoleDebugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
    consoleDebugSpy.mockRestore();
  });

  describe('Basic Rendering', () => {
    it('renders chart container when spec is valid', async () => {
      const validSpec = {
        mark: 'bar',
        encoding: {
          x: { field: 'category', type: 'ordinal' },
          y: { field: 'value', type: 'quantitative' }
        }
      };

      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: {
          spec: validSpec
        }
      });

      await flushPromises();

      expect(wrapper.find(`#${wrapper.vm.id}`).exists()).toBe(true);
    });

    it('renders error message when spec is invalid', async () => {
      const invalidSpec = {
        mark: 'invalid-mark',
        encoding: {}
      };

      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: {
          spec: invalidSpec
        }
      });

      await flushPromises();

      expect(wrapper.text()).toContain('Invalid Vega-Lite specification.');
    });

    it('renders nothing when spec validation is pending', () => {
      const wrapper = shallowMountComponent(VegaLiteWrapper);

      expect(wrapper.find('div').exists()).toBe(true);
      expect(wrapper.find(`#${wrapper.vm.id}`).exists()).toBe(false);
      expect(wrapper.text()).not.toContain('Invalid Vega-Lite specification.');
    });
  });

  describe('Props Handling', () => {
    it('accepts spec prop', () => {
      const spec = { mark: 'point' };
      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: { spec }
      });

      expect(wrapper.vm.spec).toEqual(spec);
    });

    it('accepts dataname prop', () => {
      const dataname = 'mydata';
      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: { dataname }
      });

      expect(wrapper.vm.dataname).toBe(dataname);
    });

    it('accepts data prop', () => {
      const data = [{ x: 1, y: 2 }, { x: 2, y: 4 }];
      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: { data }
      });

      expect(wrapper.vm.data).toEqual(data);
    });

    it('uses default values when props not provided', () => {
      const wrapper = shallowMountComponent(VegaLiteWrapper);

      expect(wrapper.vm.spec).toBe(null);
      expect(wrapper.vm.dataname).toBe(null);
      expect(wrapper.vm.data).toBe(null);
    });
  });

  describe('Data Properties', () => {
    it('has unique id for vega container', () => {
      const wrapper = shallowMountComponent(VegaLiteWrapper);

      expect(wrapper.vm.id).toBe('vega-lite');
    });

    it('initializes specValidation as empty object', () => {
      const wrapper = shallowMountComponent(VegaLiteWrapper);

      expect(wrapper.vm.specValidation).toEqual({});
    });
  });

  describe('Methods', () => {
    describe('validateSpec', () => {
      it('sets specValidation.valid to true for valid specs', () => {
        const validSpec = {
          mark: 'bar',
          encoding: {
            x: { field: 'category', type: 'ordinal' },
            y: { field: 'value', type: 'quantitative' }
          }
        };

        const wrapper = shallowMountComponent(VegaLiteWrapper, {
          propsData: { spec: validSpec }
        });

        wrapper.vm.validateSpec();

        expect(wrapper.vm.specValidation.valid).toBe(true);
        expect(consoleDebugSpy).toHaveBeenCalledWith('spec checks out', expect.any(Object));
      });

      it('sets specValidation.valid to false for invalid specs', () => {
        const invalidSpec = {
          invalidProperty: 'invalid'
        };

        const wrapper = shallowMountComponent(VegaLiteWrapper, {
          propsData: { spec: invalidSpec }
        });

        wrapper.vm.validateSpec();

        expect(wrapper.vm.specValidation.valid).toBe(false);
        expect(consoleWarnSpy).toHaveBeenCalledWith('Invalid spec', expect.any(Object));
      });
    });

    describe('plotSpec', () => {
      it('emits new-vega-view event with view object', async () => {
        const validSpec = {
          mark: 'bar',
          encoding: {
            x: { field: 'category', type: 'ordinal' },
            y: { field: 'value', type: 'quantitative' }
          }
        };

        const wrapper = shallowMountComponent(VegaLiteWrapper, {
          propsData: { spec: validSpec }
        });

        // Mock the element to exist in DOM
        document.body.appendChild(wrapper.element);

        await wrapper.vm.plotSpec();

        expect(wrapper.emitted('new-vega-view')).toBeTruthy();
        expect(wrapper.emitted('new-vega-view')[0][0]).toHaveProperty('insert');

        // Cleanup
        document.body.removeChild(wrapper.element);
      });

      it('does not plot when element is not in DOM', async () => {
        const validSpec = {
          mark: 'bar',
          encoding: {
            x: { field: 'category', type: 'ordinal' },
            y: { field: 'value', type: 'quantitative' }
          }
        };

        const wrapper = shallowMountComponent(VegaLiteWrapper, {
          propsData: { spec: validSpec }
        });

        // Don't add element to DOM
        await wrapper.vm.plotSpec();

        expect(wrapper.emitted('new-vega-view')).toBeFalsy();
      });

      it('inserts data when data prop is provided', async () => {
        const validSpec = {
          mark: 'bar',
          encoding: {
            x: { field: 'category', type: 'ordinal' },
            y: { field: 'value', type: 'quantitative' }
          }
        };

        const testData = [
          { category: 'A', value: 10 },
          { category: 'B', value: 20 }
        ];

        const wrapper = shallowMountComponent(VegaLiteWrapper, {
          propsData: { 
            spec: validSpec,
            data: testData
          }
        });

        document.body.appendChild(wrapper.element);

        await wrapper.vm.plotSpec();

        const mockView = wrapper.emitted('new-vega-view')[0][0];
        expect(mockView.insert).toHaveBeenCalledWith('source', testData);

        document.body.removeChild(wrapper.element);
      });
    });
  });

  describe('Watchers', () => {
    it('triggers processSpec when spec changes', async () => {
      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: { spec: { mark: 'point' } }
      });

      const processSpecSpy = vi.spyOn(wrapper.vm, 'processSpec');

      await wrapper.setProps({
        spec: { mark: 'bar' }
      });

      expect(processSpecSpy).toHaveBeenCalled();
    });
  });

  describe('Template Usage Scenarios', () => {
    // Test scenarios based on how the component is used in templates
    it('works as chart display in chart_edit.html template', async () => {
      const chartSpec = {
        mark: 'line',
        encoding: {
          x: { field: 'date', type: 'temporal' },
          y: { field: 'price', type: 'quantitative' }
        }
      };

      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: {
          spec: chartSpec
        }
      });

      await flushPromises();

      expect(wrapper.vm.spec).toEqual(chartSpec);
      expect(wrapper.find(`#${wrapper.vm.id}`).exists()).toBe(true);
    });

    it('works with dynamic data updates for interactive visualizations', async () => {
      const spec = {
        mark: 'bar',
        encoding: {
          x: { field: 'category', type: 'ordinal' },
          y: { field: 'value', type: 'quantitative' }
        }
      };

      const initialData = [{ category: 'A', value: 10 }];
      const updatedData = [
        { category: 'A', value: 10 },
        { category: 'B', value: 20 }
      ];

      const wrapper = shallowMountComponent(VegaLiteWrapper, {
        propsData: {
          spec,
          data: initialData,
          dataname: 'chartData'
        }
      });

      expect(wrapper.vm.data).toEqual(initialData);

      await wrapper.setProps({ data: updatedData });

      expect(wrapper.vm.data).toEqual(updatedData);
    });
  });
});