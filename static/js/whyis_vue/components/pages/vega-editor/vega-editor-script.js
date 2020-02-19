import Vue from 'vue'
import splitPane from 'vue-splitpane'

import vegaLiteSchema from 'vue-vega/schema/vega-lite-schema.json'

import VJsoneditor from 'v-jsoneditor'

import { validate as jsonValidate } from 'jsonschema'

import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'

import { getLocalNanopub, describeNanopub, postNewNanopub, updateNanopub, lodPrefix } from '../../../utilities/nanopub'

const defaultChartUri = 'http://example.com/example_chart'

const chartType = 'http://semanticscience.org/resource/Chart'

const chartFieldUris = {
  baseSpec: 'http://semanticscience.org/resource/hasValue',
  query: 'http://schema.org/query',
  title: 'http://purl.org/dc/terms/title',
  description: 'http://purl.org/dc/terms/description'
}

const chartPrefix = 'viz'
const chartIdLen = 16

function generateChartId (chart) {
  const intArr = new Uint8Array(chartIdLen / 2)
  window.crypto.getRandomValues(intArr)
  const chartId = Array.from(intArr, (dec) => ('0' + dec.toString(16)).substr(-2)).join('')

  return `${lodPrefix}/${chartPrefix}/${chartId}`
}

function buildChartLd (chart) {
  const chartLd = Object.entries(chart)
    .reduce((o, [field, value]) => Object.assign(o, { [chartFieldUris[field]]: [{ '@value': value }] }), {})
  chartLd[chartFieldUris.baseSpec] = JSON.stringify(chartLd[chartFieldUris.baseSpec])
  chartLd['@type'] = [chartType]
  chartLd['@id'] = generateChartId(chart)
  return chartLd
}

function extractChart (chartLd) {
  const chart = Object.entries(chartFieldUris)
    .reduce((o, [field, uri]) => Object.assign(o, { [field]: chartLd[uri][0]['@value'] }), {})
  chart.baseSpec = JSON.parse(chart.baseSpec)
  return chart
}

function loadDefaultChart () {
  return describeNanopub(defaultChartUri)
    .then((data) => data.filter((pub) => pub['@id'] === defaultChartUri)[0])
}

function loadNanopubChart (nanopubUri) {
  return describeNanopub(nanopubUri)
    .then((response) => response[0]['@graph'][0])
}

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
      urii: '',
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
      // spec.width = "container"
      // spec.height = "container"
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
    onQuerySuccess (results) {
      console.log('got results', results)
      this.results = results
    },
    onSpecJsonError () {
      console.log('bad', arguments)
    },
    loadChart () {
      const loadChartPromise = this.pageView === 'new' ? loadDefaultChart() : loadNanopubChart(this.pageUri)

      loadChartPromise.then(chartPub => {
        console.log('got the pub', chartPub)
        this.chart = extractChart(chartPub)
      })
    },
    saveChart () {
      if (this.pageView === 'new') {
        const chartLd = buildChartLd(this.chart)
        postNewNanopub(chartLd)
      }
    },
    describePub () {
      describeNanopub(this.urii)
        .then((pub) => console.log('describe pub', pub))
    },
    getLocalPub () {
      getLocalNanopub(this.urii)
        .then(resp => console.log('get pub', resp))
    }
  }
})
