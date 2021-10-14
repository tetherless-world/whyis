import { getDefaultChart, loadChart, saveChart, generateFullSpec } from 'utilities/vega-chart'

const state = () => getDefaultChart()

const actions = {
  resetChart({dispatch}) {
    dispatch('setChart', getDefaultChart())
  },
  async loadChart({dispatch}, uri) {
    const chart = await loadChart(uri)
    dispatch('setChart', chart)
  },
  setChart({commit}, chart) {
    commit('setBaseSpec', chart.baseSpec)
    commit('setQuery', chart.query)
    commit('setTitle', chart.title)
    commit('setDescription', chart.description)
    commit('setDepiction', chart.depiction)
    commit('setDownloadUrl', chart.downloadUrl)
    commit('setDataset', chart.dataset)
  }
}

const getters = {
  chart(state) {
    return state
  }
}

const mutations = {
  setBaseSpec(state, baseSpec) {
    state.baseSpec = baseSpec
  },
  setQuery(state, query) {
    state.query = query
  },
  setTitle(state, title) {
    state.title = title
  },
  setDescription(state, description) {
    state.description = description
  },
  setDepiction(state, depiction) {
    state.depiction = depiction
  },
  setDownloadUrl(state, downloadUrl) {
    state.downloadUrl = downloadUrl
  },
  setDataset(state, dataset) {
    state.dataset = dataset
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
