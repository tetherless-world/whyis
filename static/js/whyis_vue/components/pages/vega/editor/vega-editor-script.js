import Vue from 'vue'
import splitPane from 'vue-splitpane'

import VJsoneditor from 'v-jsoneditor'

import { getDefaultChart, loadChart, saveChart, buildSparqlSpec } from 'utilities/vega-chart'
import { goToView } from 'utilities/views'
import { querySparql } from 'utilities/sparql'


export default Vue.component('vega-editor', {
  components: {
    splitPane,
    VJsoneditor
  },
  data () {
    return {
      chart: {
        baseSpec: null,
        query: null,
        title: null,
        description: null
      },
      results: null,
      chartPub: null,
      specJsonEditorOpts: {
        mode: 'code',
        mainMenuBar: false
      }
    }
  },
  computed: {
    spec () {
      const spec = buildSparqlSpec(this.chart.baseSpec, this.results)
      console.log('spec changed', spec)
      return spec
    }
  },
  created () {
    this.loadChart()
  },
  methods: {
    getSparqlData () {
      querySparql(this.chart.query)
        .then(this.onQuerySuccess)
    },
    onQuerySuccess (results) {
      console.log('got results', results)
      this.results = results
    },
    onSpecJsonError () {
      console.log('bad', arguments)
    },
    loadChart () {
      let getChartPromise
      if (this.pageView === 'new') {
        getChartPromise = Promise.resolve(getDefaultChart())
      } else {
        getChartPromise = loadChart(this.pageUri)
      }
      getChartPromise
        .then(chart => {
          this.chart = chart
          this.getSparqlData()
        })
    },
    saveChart () {
      console.log(this.chart)
      saveChart(this.chart)
        .then(() => goToView(this.chart.uri, 'edit'))
    }
  }
})
