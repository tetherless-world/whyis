/**
 * Test helper utilities for Vue component testing
 */

import { mount, shallowMount, createLocalVue } from '@vue/test-utils';
import * as VueMaterial from 'vue-material';

/**
 * Create a local Vue instance with Material Design components
 * @returns {Vue} Local Vue instance for testing
 */
export function createTestVue() {
  const localVue = createLocalVue();
  localVue.use(VueMaterial.default);
  return localVue;
}

/**
 * Mount a Vue component with standard test configuration
 * @param {Object} component - Vue component to mount
 * @param {Object} options - Mounting options
 * @returns {Wrapper} Vue Test Utils wrapper
 */
export function mountComponent(component, options = {}) {
  const localVue = createTestVue();
  
  return mount(component, {
    localVue,
    ...options
  });
}

/**
 * Shallow mount a Vue component with standard test configuration
 * @param {Object} component - Vue component to shallow mount
 * @param {Object} options - Mounting options
 * @returns {Wrapper} Vue Test Utils wrapper
 */
export function shallowMountComponent(component, options = {}) {
  const localVue = createTestVue();
  
  return shallowMount(component, {
    localVue,
    ...options
  });
}

/**
 * Create mock props for components based on common template usage patterns
 */
export const mockProps = {
  // Common props from template usage
  uri: 'http://example.org/resource/test',
  label: 'Test Label',
  active: false,
  loading: false,
  instances: 'http://example.org/resource/test',
  
  // Chart/visualization props
  spec: {
    mark: 'bar',
    encoding: {
      x: { field: 'category', type: 'ordinal' },
      y: { field: 'value', type: 'quantitative' }
    }
  },
  data: [
    { category: 'A', value: 10 },
    { category: 'B', value: 20 },
    { category: 'C', value: 15 }
  ]
};

/**
 * Wait for Vue's next tick and any pending DOM updates
 */
export async function flushPromises() {
  await new Promise(resolve => setTimeout(resolve, 0));
}