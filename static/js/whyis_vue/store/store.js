import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

import vizEditor from './modules/viz-editor'
import bobViz from './modules/bob-viz'

Vue.use(Vuex)

export const store = new Vuex.Store({
  modules: {
    bobViz,
    vizEditor
  },
  plugins: [
    createPersistedState({
      paths: ['vizEditor'],
    }),
  ],
})
