/**
 * @jest-environment jsdom
 */

import { createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';

// Mock vuex-persistedstate to avoid localStorage issues in tests
jest.mock('vuex-persistedstate', () => {
  return jest.fn(() => () => {});
});

// Mock the viz-editor module
jest.mock('../../js/whyis_vue/store/viz-editor', () => ({
  state: () => ({
    uri: null,
    baseSpec: {},
    query: '',
    title: 'Test Chart'
  }),
  mutations: {},
  actions: {},
  getters: {}
}));

describe('Vuex store main configuration', () => {
  let localVue;

  beforeEach(() => {
    localVue = createLocalVue();
    localVue.use(Vuex);
    jest.clearAllMocks();
  });

  test('should create store instance', () => {
    // Import after mocks are set up
    const { store } = require('../../js/whyis_vue/store/index');
    
    expect(store).toBeDefined();
    expect(store).toBeInstanceOf(Vuex.Store);
  });

  test('should include vizEditor module', () => {
    const { store } = require('../../js/whyis_vue/store/index');
    
    expect(store.state.vizEditor).toBeDefined();
  });

  test('should have vizEditor state initialized', () => {
    const { store } = require('../../js/whyis_vue/store/index');
    
    expect(store.state.vizEditor.title).toBe('Test Chart');
  });

  test('should use createPersistedState plugin', () => {
    const createPersistedState = require('vuex-persistedstate');
    
    // Force re-import to trigger plugin initialization
    jest.resetModules();
    jest.mock('vuex-persistedstate', () => {
      return jest.fn(() => () => {});
    });
    
    require('../../js/whyis_vue/store/index');
    
    // Verify the plugin factory was called
    const mockPlugin = require('vuex-persistedstate');
    expect(mockPlugin).toHaveBeenCalled();
  });

  test('store should be exportable', () => {
    const storeModule = require('../../js/whyis_vue/store/index');
    
    expect(storeModule.store).toBeDefined();
    expect(typeof storeModule.store).toBe('object');
  });
});
