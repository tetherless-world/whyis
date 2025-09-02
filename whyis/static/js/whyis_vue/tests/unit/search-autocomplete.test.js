/**
 * Unit tests for SearchAutocomplete component
 * Tests the search autocomplete component used in the main navigation
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { shallowMountComponent, flushPromises } from '../helpers/test-utils.js';
import SearchAutocomplete from '../../components/search-autocomplete.vue';

// Mock axios for HTTP requests
const mockAxios = {
  get: vi.fn(() => Promise.resolve({
    data: [
      { node: 'http://example.org/entity1', label: 'Entity 1', preflabel: 'Entity 1' },
      { node: 'http://example.org/entity2', label: 'Entity 2', preflabel: 'Preferred Entity 2' }
    ]
  }))
};

describe('SearchAutocomplete Component', () => {
  beforeEach(() => {
    // Mock window.encodeURIComponent
    global.encodeURIComponent = vi.fn((str) => str);
    
    // Reset axios mock
    mockAxios.get.mockClear();
  });

  describe('Basic Rendering', () => {
    it('renders autocomplete input', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      expect(wrapper.find('md-autocomplete').exists()).toBe(true);
      expect(wrapper.find('label').text()).toBe('Search');
    });

    it('renders hidden input for form submission', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      const hiddenInput = wrapper.find('input[type="hidden"]');
      expect(hiddenInput.exists()).toBe(true);
      expect(hiddenInput.attributes('name')).toBe('search');
    });

    it('has correct CSS class', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      expect(wrapper.find('.search').exists()).toBe(true);
    });
  });

  describe('Data Properties', () => {
    it('initializes with correct default data', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      expect(wrapper.vm.query).toBe(null);
      expect(wrapper.vm.selected).toBe(null);
      expect(wrapper.vm.items).toEqual([]);
    });
  });

  describe('Props', () => {
    it('accepts root_url prop', () => {
      const rootUrl = 'http://example.org/';
      const wrapper = shallowMountComponent(SearchAutocomplete, {
        propsData: { root_url: rootUrl }
      });

      expect(wrapper.vm.root_url).toBe(rootUrl);
    });

    it('accepts axios prop', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete, {
        propsData: { axios: mockAxios }
      });

      expect(wrapper.vm.axios).toBe(mockAxios);
    });
  });

  describe('Methods', () => {
    describe('resolveEntity', () => {
      it('makes axios request with correct parameters', async () => {
        // Mock axios in global scope for the component
        global.axios = mockAxios;

        const wrapper = shallowMountComponent(SearchAutocomplete);
        const searchTerm = 'test';

        await wrapper.vm.resolveEntity(searchTerm);

        expect(mockAxios.get).toHaveBeenCalledWith('/', {
          params: { view: 'resolve', term: 'test*' },
          responseType: 'json'
        });
      });

      it('processes response data correctly', async () => {
        global.axios = mockAxios;

        const wrapper = shallowMountComponent(SearchAutocomplete);
        
        const result = await wrapper.vm.resolveEntity('test');
        const items = await result; // The method returns a promise

        expect(items).toHaveLength(2);
        expect(items[0]).toHaveProperty('toLowerCase');
        expect(items[0]).toHaveProperty('toString');
        expect(items[0].toLowerCase()).toBe('entity 1');
        expect(items[0].toString()).toBe('Entity 1');
      });

      it('adds wildcard to search term', async () => {
        global.axios = mockAxios;

        const wrapper = shallowMountComponent(SearchAutocomplete);
        
        await wrapper.vm.resolveEntity('partial');

        expect(mockAxios.get).toHaveBeenCalledWith('/', {
          params: { view: 'resolve', term: 'partial*' },
          responseType: 'json'
        });
      });
    });

    describe('selectedItemChange', () => {
      it('navigates to entity view page', () => {
        const wrapper = shallowMountComponent(SearchAutocomplete);
        const testItem = {
          node: 'http://example.org/entity1',
          label: 'Test Entity'
        };

        wrapper.vm.selectedItemChange(testItem);

        expect(global.encodeURIComponent).toHaveBeenCalledWith('http://example.org/entity1');
        expect(global.window.location.href).toBe('/about?view=view&uri=http://example.org/entity1');
      });

      it('handles URI encoding for special characters', () => {
        const wrapper = shallowMountComponent(SearchAutocomplete);
        const testItem = {
          node: 'http://example.org/entity with spaces',
          label: 'Test Entity'
        };

        wrapper.vm.selectedItemChange(testItem);

        expect(global.encodeURIComponent).toHaveBeenCalledWith('http://example.org/entity with spaces');
      });
    });
  });

  describe('Template Integration', () => {
    it('binds model correctly', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      expect(wrapper.find('md-autocomplete').attributes('md-input-name')).toBe('query');
      expect(wrapper.find('md-autocomplete').attributes('md-layout')).toBe('box');
    });

    it('displays items in autocomplete', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      // Set items data
      wrapper.setData({
        items: [
          { node: 'uri1', label: 'Item 1', preflabel: 'Item 1' },
          { node: 'uri2', label: 'Item 2', preflabel: 'Preferred Item 2' }
        ]
      });

      expect(wrapper.find('md-autocomplete').attributes(':md-options')).toBe('items');
    });

    it('handles preferred label display logic', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      // The template should show preferred label when different from label
      // This is tested through the template structure
      expect(wrapper.html()).toContain('v-if="item.label != item.preflabel"');
      expect(wrapper.html()).toContain('(preferred: {{item.preflabel}})');
    });
  });

  describe('Template Usage Scenarios', () => {
    // Test scenarios based on how the component is used in base_vue.html
    it('works as main navigation search in base template', async () => {
      global.axios = mockAxios;

      const wrapper = shallowMountComponent(SearchAutocomplete);

      // Simulate user typing
      await wrapper.vm.resolveEntity('knowledge');

      expect(mockAxios.get).toHaveBeenCalledWith('/', {
        params: { view: 'resolve', term: 'knowledge*' },
        responseType: 'json'
      });
    });

    it('integrates with form submission', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      // Set query value
      wrapper.setData({ query: 'search term' });

      const hiddenInput = wrapper.find('input[name="search"]');
      expect(hiddenInput.element.value).toBe('search term');
    });

    it('handles entity selection and navigation', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);

      const selectedEntity = {
        node: 'http://example.org/resource/123',
        label: 'Research Paper',
        preflabel: 'Research Paper'
      };

      wrapper.vm.selectedItemChange(selectedEntity);

      expect(global.window.location.href).toBe('/about?view=view&uri=http://example.org/resource/123');
    });
  });

  describe('Event Handling', () => {
    it('handles md-changed event', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);
      const resolveEntitySpy = vi.spyOn(wrapper.vm, 'resolveEntity');

      // Simulate the md-changed event
      wrapper.find('md-autocomplete').vm.$emit('md-changed', 'test query');

      expect(resolveEntitySpy).toHaveBeenCalledWith('test query');
    });

    it('handles md-selected event', () => {
      const wrapper = shallowMountComponent(SearchAutocomplete);
      const selectedItemChangeSpy = vi.spyOn(wrapper.vm, 'selectedItemChange');

      const testItem = { node: 'test-uri', label: 'Test' };

      // Simulate the md-selected event
      wrapper.find('md-autocomplete').vm.$emit('md-selected', testItem);

      expect(selectedItemChangeSpy).toHaveBeenCalledWith(testItem);
    });
  });
});