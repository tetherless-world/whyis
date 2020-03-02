import Vue from 'vue'
import splitPane from 'vue-splitpane'

import vegaLiteSchema from 'vue-vega/schema/vega-lite-schema.json'

import VJsoneditor from 'v-jsoneditor'

import { validate as jsonValidate } from 'jsonschema'

import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'

import { getDefaultChart, loadChart, saveChart } from '../../../utilities/vega-chart'
import { goToView } from '../../../utilities/views'
import { querySparql } from '../../../utilities/sparql'

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
        schema: vegaLiteSchema,
        mode: 'code',
        mainMenuBar: false
      }
    }
  },
  computed: {
    data () {
      const data = []
      if (this.results) {
        for (const row of this.results.results.bindings) {
          const resultData = {}
          data.push(resultData)
          Object.entries(row).forEach(([field, result, t]) => {
            let value = result.value
            if (result.type === 'literal' && result.datatype) {
              value = fromRdf(literal(value, namedNode(result.datatype)))
            }
            resultData[field] = value
          })
        }
      }
      return data
    },
    spec () {
      if (!this.chart.baseSpec) {
        return null
      }
      const spec = Object.assign({}, this.chart.baseSpec)
      spec.data = { values: this.data }
      console.log('spec changed', spec)
      const validation = jsonValidate(spec, vegaLiteSchema)
      if (!validation.valid) {
        console.warn('Invalid schema', validation)
      }
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
