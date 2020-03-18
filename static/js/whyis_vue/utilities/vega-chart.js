
import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'

import { listNanopubs, getLocalNanopub, describeNanopub, postNewNanopub, deleteNanopub, lodPrefix } from './nanopub'

const defaultQuery = `
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?c (MIN(?class) AS ?class) (COUNT(?x) AS ?count)
WHERE {
    ?x a ?c.
    ?c rdfs:label ?class.
}
GROUP BY ?c
ORDER BY DESC(?count)
`.trim()

const defaultSpec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
  "mark": "bar",
  "encoding": {
    "x": {
      "field": "count",
      "type": "quantitative"
    },
    "y": {
      "field": "class",
      "type": "ordinal"
    }
  }
}

const defaultChart = {
  baseSpec: defaultSpec,
  query: defaultQuery,
  title: 'Example Bar Chart',
  description: 'An example chart that looks up the frequency for each class in the knowledge graph.'
}

const chartType = 'http://semanticscience.org/resource/Chart'

const chartFieldUris = {
  baseSpec: 'http://semanticscience.org/resource/hasValue',
  query: 'http://schema.org/query',
  title: 'http://purl.org/dc/terms/title',
  description: 'http://purl.org/dc/terms/description'
}

const chartPrefix = 'viz'
const chartIdLen = 16

function generateChartId () {
  const intArr = new Uint8Array(chartIdLen / 2)
  window.crypto.getRandomValues(intArr)
  const chartId = Array.from(intArr, (dec) => ('0' + dec.toString(16)).substr(-2)).join('')

  return `${lodPrefix}/${chartPrefix}/${chartId}`
}

function buildChartLd (chart) {
  chart = Object.assign({}, chart)
  chart.baseSpec = JSON.stringify(chart.baseSpec)
  const chartLd = Object.entries(chart)
    .reduce((o, [field, value]) => Object.assign(o, { [chartFieldUris[field]]: [{ '@value': value }] }), {})
  chartLd['@type'] = [chartType]
  chartLd['@id'] = chart.uri
  return chartLd
}

function extractChart (chartLd) {
  const chart = Object.entries(chartFieldUris)
    .reduce((o, [field, uri]) => Object.assign(o, { [field]: chartLd[uri][0]['@value'] }), {})
  chart.baseSpec = JSON.parse(chart.baseSpec)
  chart.uri = chartLd['@id']

  return chart
}

function getDefaultChart () {
  return Object.assign({}, defaultChart)
}

function loadChartFromNanopub(nanopubUri, chartUri) {
  return describeNanopub(nanopubUri)
    .then((describeData) => {
      const graphs = describeData.filter(obj => chartUri.startsWith(obj['@id']) && typeof(obj['@graph']) === 'object')
      if (graphs.length === 0) {
        return
      }
      const charts = graphs[0]['@graph'].filter(obj => obj['@id'] === chartUri)
      if (charts.length > 0) {
        return extractChart(charts[0])
      }
    })
}

function loadChart (chartUri) {
  return listNanopubs(chartUri)
    .then(nanopubs => {
      if (nanopubs.length > 0) {
        const nanopubUri = nanopubs[0].np
        return loadChartFromNanopub(nanopubUri, chartUri)
      }
    })
}

function saveChart (chart) {
  let deletePromise = Promise.resolve()
  if (chart.uri) {
    deletePromise = deleteChart(chart.uri)
  } else {
    chart.uri = generateChartId()
  }
  const chartLd = buildChartLd(chart)
  return deletePromise
    .then(() => postNewNanopub(chartLd))
}

function deleteChart (chartUri) {
  return listNanopubs(chartUri)
    .then(nanopubs => Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np))))
}

function transformSparqlData (sparqlResults) {
  const data = []
  if (sparqlResults) {
    for (const row of sparqlResults.results.bindings) {
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
}

function buildSparqlSpec (baseSpec, sparqlResults) {
  if (!baseSpec) {
    return null
  }
  const spec = Object.assign({}, baseSpec)
  spec.data = { values: transformSparqlData(sparqlResults) }
  return spec
}

export { getDefaultChart, loadChart, saveChart, buildSparqlSpec}
