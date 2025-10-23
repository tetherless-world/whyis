/**
 * @jest-environment jsdom
 */

import { createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import vizEditorModule from '../../js/whyis_vue/store/viz-editor';

// Mock the vega-chart utilities
jest.mock('../../js/whyis_vue/utilities/vega-chart', () => ({
  getDefaultChart: jest.fn(() => ({
    uri: null,
    baseSpec: {
      "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
      "mark": "bar",
      "encoding": {}
    },
    query: 'SELECT * WHERE { ?s ?p ?o }',
    title: 'Test Chart',
    description: 'Test Description',
    depiction: null
  })),
  loadChart: jest.fn((uri) => Promise.resolve({
    uri: uri,
    baseSpec: { mark: 'line' },
    query: 'SELECT * WHERE { ?s ?p ?o }',
    title: 'Loaded Chart',
    description: 'Loaded Description',
    depiction: null
  })),
  saveChart: jest.fn((chart) => Promise.resolve(chart)),
  buildSparqlSpec: jest.fn((baseSpec, data) => ({ ...baseSpec, data: { values: data } }))
}));

const { getDefaultChart, loadChart } = require('../../js/whyis_vue/utilities/vega-chart');

describe('viz-editor store module', () => {
  let localVue;
  let store;

  beforeEach(() => {
    localVue = createLocalVue();
    localVue.use(Vuex);
    
    // Clear mock calls
    jest.clearAllMocks();
    
    // Create a fresh store instance for each test
    store = new Vuex.Store({
      modules: {
        vizEditor: {
          namespaced: true,
          ...vizEditorModule
        }
      }
    });
  });

  describe('initial state', () => {
    test('should initialize with default chart', () => {
      const state = store.state.vizEditor;
      expect(state).toBeDefined();
      expect(state.baseSpec).toBeDefined();
      expect(state.query).toBeDefined();
      expect(state.title).toBeDefined();
    });
  });

  describe('mutations', () => {
    test('setBaseSpec should update base specification', () => {
      const newSpec = { mark: 'point', encoding: {} };
      store.commit('vizEditor/setBaseSpec', newSpec);
      
      expect(store.state.vizEditor.baseSpec).toEqual(newSpec);
    });

    test('setQuery should update SPARQL query', () => {
      const newQuery = 'SELECT ?x WHERE { ?x a <Type> }';
      store.commit('vizEditor/setQuery', newQuery);
      
      expect(store.state.vizEditor.query).toBe(newQuery);
    });
  });

  describe('getters', () => {
    test('chart getter should return complete chart state', () => {
      const chart = store.getters['vizEditor/chart'];
      
      expect(chart).toBeDefined();
      expect(chart.baseSpec).toBeDefined();
      expect(chart.query).toBeDefined();
      expect(chart.title).toBeDefined();
    });
  });

  describe('actions', () => {
    test('resetChart should reset to default chart', async () => {
      // First modify the state
      store.commit('vizEditor/setQuery', 'MODIFIED QUERY');
      
      // Then reset
      await store.dispatch('vizEditor/resetChart');
      
      expect(getDefaultChart).toHaveBeenCalled();
      // State should be reset to default
      const state = store.state.vizEditor;
      expect(state.title).toBe('Test Chart');
    });

    test('loadChart should load chart from URI', async () => {
      const testUri = 'http://example.org/chart/123';
      
      await store.dispatch('vizEditor/loadChart', testUri);
      
      expect(loadChart).toHaveBeenCalledWith(testUri);
      
      const state = store.state.vizEditor;
      expect(state.uri).toBe(testUri);
      expect(state.title).toBe('Loaded Chart');
      expect(state.description).toBe('Loaded Description');
    });

    test('loadChart should handle loading errors gracefully', async () => {
      loadChart.mockRejectedValueOnce(new Error('Failed to load'));
      
      await expect(
        store.dispatch('vizEditor/loadChart', 'invalid-uri')
      ).rejects.toThrow('Failed to load');
    });
  });

  describe('integration', () => {
    test('should allow chaining mutations and actions', async () => {
      // Set initial values
      store.commit('vizEditor/setQuery', 'INITIAL QUERY');
      store.commit('vizEditor/setBaseSpec', { mark: 'area' });
      
      // Reset
      await store.dispatch('vizEditor/resetChart');
      
      // Load a chart
      await store.dispatch('vizEditor/loadChart', 'http://example.org/test');
      
      const state = store.state.vizEditor;
      expect(state.uri).toBe('http://example.org/test');
      expect(state.title).toBe('Loaded Chart');
    });
  });
});
