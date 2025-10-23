/**
 * @jest-environment jsdom
 */

import { createLocalVue, shallowMount } from '@vue/test-utils';
import viewMixin from '../../js/whyis_vue/mixins/view-mixin';

// Create a test component that uses the mixin
const TestComponent = {
  mixins: [viewMixin],
  template: '<div>Test Component</div>'
};

describe('view-mixin', () => {
  let localVue;
  let wrapper;
  let originalLocation;

  beforeEach(() => {
    localVue = createLocalVue();
    // Set up window globals
    window.NODE_URI = 'http://example.org/test-resource';
    
    // Save original location
    originalLocation = window.location;
    
    // Mock location with URLSearchParams support
    delete window.location;
    window.location = {
      search: '',
      href: 'http://localhost/'
    };
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy();
    }
    // Restore original location
    window.location = originalLocation;
  });

  test('should provide DEFAULT_VIEWS in component data', () => {
    wrapper = shallowMount(TestComponent, { localVue });
    
    expect(wrapper.vm.DEFAULT_VIEWS).toBeDefined();
    expect(wrapper.vm.DEFAULT_VIEWS.NEW).toBe('new');
    expect(wrapper.vm.DEFAULT_VIEWS.EDIT).toBe('edit');
    expect(wrapper.vm.DEFAULT_VIEWS.VIEW).toBe('view');
  });

  test('should provide pageUri computed property', () => {
    window.NODE_URI = 'http://example.org/custom-uri';
    wrapper = shallowMount(TestComponent, { localVue });
    
    expect(wrapper.vm.pageUri).toBe('http://example.org/custom-uri');
  });

  test('should provide pageView computed property', () => {
    window.location.search = '?view=new&uri=test';
    wrapper = shallowMount(TestComponent, { localVue });
    
    expect(wrapper.vm.pageView).toBe('new');
  });

  test('should return null for pageView when no view param', () => {
    window.location.search = '?uri=test';
    wrapper = shallowMount(TestComponent, { localVue });
    
    expect(wrapper.vm.pageView).toBeNull();
  });

  test('should make DEFAULT_VIEWS immutable', () => {
    wrapper = shallowMount(TestComponent, { localVue });
    
    // Attempt to modify should not affect the original
    expect(() => {
      wrapper.vm.DEFAULT_VIEWS.NEW = 'changed';
    }).toThrow();
  });

  test('should be usable in multiple components without conflicts', () => {
    const wrapper1 = shallowMount(TestComponent, { localVue });
    const wrapper2 = shallowMount(TestComponent, { localVue });
    
    expect(wrapper1.vm.DEFAULT_VIEWS).toEqual(wrapper2.vm.DEFAULT_VIEWS);
    expect(wrapper1.vm.pageUri).toBe(wrapper2.vm.pageUri);
    
    wrapper1.destroy();
    wrapper2.destroy();
  });
});
