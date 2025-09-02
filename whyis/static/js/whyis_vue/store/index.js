/**
 * Main Vuex store configuration for the Whyis Vue application.
 * Provides centralized state management with persistence capabilities.
 * 
 * @module store
 */

import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

import vizEditor from './viz-editor'

Vue.use(Vuex)

/**
 * Main Vuex store instance with modules and persistence
 * @constant {Vuex.Store} store - Configured Vuex store with:
 * - vizEditor module for chart/visualization editing state
 * - Persistent state plugin to maintain state across sessions
 */
export const store = new Vuex.Store({
  modules: {
    vizEditor
  },
  plugins: [createPersistedState()],
})
