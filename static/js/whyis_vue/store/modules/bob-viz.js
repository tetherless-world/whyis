import { getDefaultChart, generateFullSpec, transformSparqlData } from 'utilities/vega-chart'
import { querySparql } from 'utilities/sparql'

const {query: defaultQuery} = getDefaultChart()

const state = () => ({
  query: defaultQuery,
  results: null,
})

const actions = {
  // setters
  setResults: ({commit}, results) => commit('setResults', results),
  setQuery: ({commit}, query) => commit('setQuery', query),

  /**
   * Execute the given query, setting both results and query state
  */
  async executeQuery({dispatch}, query) {
    dispatch('setQuery', query)
    dispatch('setResults', await querySparql(query))
  }
}

const getters = {
  // basic getters
  query: state => state.query,
  results: state => state.results,

  /**
   * Get results formatted as a vega dataset
   */
  vegaData(state) {
    if (!state.results) {
      return null
    }
    return {
      values: transformSparqlData(state.results)
    }
  }
}

const mutations = {
  setResults(state, results) {
    state.results = results
  },
  setQuery(state, query) {
    state.query = query
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
