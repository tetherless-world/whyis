
import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'

import { listNanopubs, getLocalNanopub, describeNanopub, postNewNanopub, deleteNanopub, lodPrefix } from 'utilities/nanopub'
import { querySparql } from 'utilities/sparql'

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
    .reduce((o, [field, value]) => {
      if (chartFieldUris[field]) {
        Object.assign(o, { [chartFieldUris[field]]: [{ '@value': value }] })
      }
      return o
    }, {})
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
      const assertion_id = `${nanopubUri}_assertion`
      for (let graph of describeData) {
        if (graph['@id'] === assertion_id) {
          for (let resource of graph['@graph']) {
            if (resource['@id'] === chartUri) {
              return extractChart(resource)
            }
          }
        }
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
  console.log('Deleting chart', chartUri)
  return listNanopubs(chartUri)
    .then(nanopubs => Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np))))
}

const chartQuery = `
  PREFIX dcterms: <http://purl.org/dc/terms/>
  PREFIX schema: <http://schema.org/>
  PREFIX sio: <http://semanticscience.org/resource/>
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  SELECT DISTINCT ?chart ?title ?description ?query ?baseSpec
  WHERE {
    ?chart a sio:Chart .
    ?chart dcterms:title ?title .
    ?chart dcterms:description ?description .
    ?chart schema:query ?query .
    ?chart sio:hasValue ?baseSpec
  }
  `

function getCharts () {
  return querySparql(chartQuery)
    .then(data =>
      data.results.bindings.map((chartResult) => {
        const chart = Object.entries(chartResult)
          .reduce((o, [field, value]) => {
            o[field] = value.value
            return o
          }, {})
        chart.uri = chart.chart
        delete chart.chart
        chart.baseSpec = JSON.parse(chart.baseSpec)
        return chart
      })
    )

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

export { getDefaultChart, loadChart, saveChart, getCharts, buildSparqlSpec}
