/**
 * Unit tests for Spinner component
 * Tests the loading spinner utility component used throughout the application
 */

import { describe, it, expect } from 'vitest';
import { shallowMountComponent } from '../helpers/test-utils.js';
import Spinner from '../../components/utils/spinner.vue';

describe('Spinner Component', () => {
  describe('Basic Rendering', () => {
    it('renders spinner when loading is true', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true
        }
      });

      expect(wrapper.find('.spinner').exists()).toBe(true);
      expect(wrapper.find('.spinner').isVisible()).toBe(true);
    });

    it('hides spinner when loading is false', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: false
        }
      });

      expect(wrapper.find('.spinner').exists()).toBe(true);
      expect(wrapper.find('.spinner').isVisible()).toBe(false);
    });

    it('renders three spinning dots', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true
        }
      });

      const dots = wrapper.findAll('.sync');
      expect(dots.length).toBe(3);
    });
  });

  describe('Props Configuration', () => {
    it('displays text when provided', () => {
      const testText = 'Loading data...';
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          text: testText
        }
      });

      expect(wrapper.text()).toContain(testText);
    });

    it('does not display text when not provided', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true
        }
      });

      expect(wrapper.find('[style*="font-size:1.5rem"]').exists()).toBe(false);
    });

    it('applies custom color to spinner dots', () => {
      const customColor = '#ff0000';
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          color: customColor
        }
      });

      // Check that the component data contains the custom color
      expect(wrapper.vm.spinnerStyle.backgroundColor).toBe(customColor);
    });

    it('applies custom size to spinner dots', () => {
      const customSize = '20px';
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          size: customSize
        }
      });

      expect(wrapper.vm.spinnerStyle.width).toBe(customSize);
      expect(wrapper.vm.spinnerStyle.height).toBe(customSize);
    });

    it('applies custom margin to spinner dots', () => {
      const customMargin = '5px';
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          margin: customMargin
        }
      });

      expect(wrapper.vm.spinnerStyle.margin).toBe(customMargin);
    });

    it('applies custom border radius to spinner dots', () => {
      const customRadius = '50%';
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          radius: customRadius
        }
      });

      expect(wrapper.vm.spinnerStyle.borderRadius).toBe(customRadius);
    });
  });

  describe('Default Props', () => {
    it('uses default props when none provided', () => {
      const wrapper = shallowMountComponent(Spinner);

      expect(wrapper.vm.loading).toBe(true); // default loading state
      expect(wrapper.vm.color).toBe('#08233c'); // default color
      expect(wrapper.vm.size).toBe('15px'); // default size
      expect(wrapper.vm.margin).toBe('2px'); // default margin
      expect(wrapper.vm.radius).toBe('100%'); // default radius
      expect(wrapper.vm.text).toBe(null); // default text
    });
  });

  describe('Animation Delays', () => {
    it('applies different animation delays to each dot', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true
        }
      });

      expect(wrapper.vm.spinnerDelay1.animationDelay).toBe('0.07s');
      expect(wrapper.vm.spinnerDelay2.animationDelay).toBe('0.14s');
      expect(wrapper.vm.spinnerDelay3.animationDelay).toBe('0.21s');
    });
  });

  describe('Template Usage Scenarios', () => {
    // Test scenarios based on how the component is used in templates
    it('works as loading indicator for data operations', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          text: 'Loading chart data...',
          color: '#2196F3' // Material blue
        }
      });

      expect(wrapper.isVisible()).toBe(true);
      expect(wrapper.text()).toContain('Loading chart data...');
    });

    it('works as loading indicator for file uploads', () => {
      const wrapper = shallowMountComponent(Spinner, {
        propsData: {
          loading: true,
          text: 'Uploading file...',
          size: '20px'
        }
      });

      expect(wrapper.isVisible()).toBe(true);
      expect(wrapper.text()).toContain('Uploading file...');
      expect(wrapper.vm.size).toBe('20px');
    });
  });
});