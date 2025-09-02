/**
 * Vuex store module for managing visualization editor state.
 * Handles chart creation, editing, loading, and persistence for the Vega-Lite chart editor.
 * 
 * @module viz-editor
 */

import { getDefaultChart, loadChart, saveChart, buildSparqlSpec } from '../utilities/vega-chart'

/**
 * Initial state factory function that returns a default chart object
 * @returns {Object} Default chart state with empty values
 */
const state = () => getDefaultChart()

/**
 * Vuex actions for async operations and business logic
 * @namespace actions
 */
const actions = {
  /**
   * Resets the chart to its default state
   * @param {Object} context - Vuex action context
   * @param {Function} context.commit - Mutation commit function
   */
  resetChart({commit}) {
    commit('setChart', getDefaultChart())
  },
  
  /**
   * Loads a chart from the knowledge graph by URI
   * @param {Object} context - Vuex action context
   * @param {Function} context.commit - Mutation commit function
   * @param {string} uri - URI of the chart to load
   * @returns {Promise} Promise that resolves when chart is loaded
   */
  async loadChart({commit}, uri) {
    const chart = await loadChart(uri)
    commit('setChart', chart)
  }
}

/**
 * Vuex getters for computed state properties
 * @namespace getters
 */
const getters = {
  /**
   * Returns the complete chart state
   * @param {Object} state - Current module state
   * @returns {Object} The complete chart object
   */
  chart(state) {
    return state
  }
}

/**
 * Vuex mutations for synchronous state updates
 * @namespace mutations
 */
const mutations = {
  /**
   * Updates the Vega-Lite base specification
   * @param {Object} state - Current module state
   * @param {Object} baseSpec - New Vega-Lite specification object
   */
  setBaseSpec(state, baseSpec) {
    state.baseSpec = baseSpec
  },
  
  /**
   * Updates the SPARQL query string
   * @param {Object} state - Current module state
   * @param {string} query - New SPARQL query string
   */
  setQuery(state, query) {
    state.query = query
  },
  
  /**
   * Updates the chart title
   * @param {Object} state - Current module state
   * @param {string} title - New chart title
   */
  setTitle(state, title) {
    state.title = title
  },
  
  /**
   * Updates the chart description
   * @param {Object} state - Current module state
   * @param {string} description - New chart description
   */
  setDescription(state, description) {
    state.description = description
  },
  
  /**
   * Updates the chart depiction/preview image
   * @param {Object} state - Current module state
   * @param {string} depiction - New depiction URI
   */
  setDepiction(state, depiction) {
    state.depiction = depiction
  },
  
  /**
   * Replaces the entire chart state with a new chart object
   * @param {Object} state - Current module state
   * @param {Object} chart - New chart object to merge into state
   */
  setChart(state, chart) {
    Object.assign(state, chart)
  },
}

/**
 * Vuex module configuration
 * @type {Object}
 * @property {boolean} namespaced - Enables namespacing for this module
 * @property {Function} state - State factory function
 * @property {Object} getters - Module getters
 * @property {Object} actions - Module actions
 * @property {Object} mutations - Module mutations
 */
export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
