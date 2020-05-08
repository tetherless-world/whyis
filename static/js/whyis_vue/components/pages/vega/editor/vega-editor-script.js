import Vue from 'vue'
import splitPane from 'vue-splitpane'
import VJsoneditor from 'v-jsoneditor'
import deepEquals from 'fast-deep-equal'

import { getDefaultChart, loadChart, saveChart, buildSparqlSpec } from 'utilities/vega-chart'
import { getViewUrl, goToView } from 'utilities/views'
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
      },
      discardChangesDialogActive: false,
      discardChangesUrl: '',
    }
  },
  computed: {
    saveLabel () {
      return this.unsavedChanges
        ? 'Save visualization'
        : 'No changes need to be saved'
    },
    spec () {
      const spec = buildSparqlSpec(this.chart.baseSpec, this.results)
      console.log('spec changed', spec)
      return spec
    },
    toolButtons () {
      switch (this.pageView) {
        case 'new':
          return ['save']
        case 'edit':
          return ['save', 'view']
        default:
          throw `Unsupported view ${this.pageView}`
      }
    },
    unsavedChanges () {
      return this.pageView === 'new' || !deepEquals(this.chart, this.originalChart)
    },
    viewVisUrl () {
      return getViewUrl(this.pageUri, 'view')
    }
  },
  created () {
    this.loadChart()
  },
  methods: {
    discardChangesAndGo () {
      window.location = this.discardChangesUrl
    },
    getSparqlData () {
      querySparql(this.chart.query)
        .then(this.onQuerySuccess)
    },
    onNavClick ($event) {
      if (this.unsavedChanges) {
        $event.preventDefault()
        this.discardChangesUrl = $event.currentTarget.href
        this.discardChangesDialogActive = true
      }
    },
    onQuerySuccess (results) {
      console.log('got results', results)
      this.results = results
    },
    onSpecJsonError () {
      console.log('bad', arguments)
    },
    async onNewVegaView (view) {
      const blob = await view.toImageURL('png')
        .then(url => fetch(url))
        .then(resp => resp.blob())
      const fr = new FileReader()
      fr.addEventListener('load', () => {
        this.chart.depiction = fr.result
        // document.getElementById('page')
        //   .appendChild(jQuery.parseHTML(`<img src="${fr.result}">`)[0])
      })
      fr.readAsDataURL(blob)
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
          this.originalChart = JSON.parse(JSON.stringify(chart))
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
