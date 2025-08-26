import { defineStore } from 'pinia'
import { getDefaultChart, loadChart, saveChart, buildSparqlSpec } from '../utilities/vega-chart'

export const useVizEditorStore = defineStore('vizEditor', {
  state: () => getDefaultChart(),
  
  getters: {
    chart: (state) => state
  },
  
  actions: {
    resetChart() {
      Object.assign(this, getDefaultChart())
    },
    
    async loadChart(uri) {
      const chart = await loadChart(uri)
      Object.assign(this, chart)
    },
    
    setBaseSpec(baseSpec) {
      this.baseSpec = baseSpec
    },
    
    setQuery(query) {
      this.query = query
    },
    
    setTitle(title) {
      this.title = title
    },
    
    setDescription(description) {
      this.description = description
    },
    
    setDepiction(depiction) {
      this.depiction = depiction
    },
    
    setChart(chart) {
      Object.assign(this, chart)
    }
  }
})
