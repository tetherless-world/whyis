
import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'
import axios from 'axios'
import Papa from 'papaparse'

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
  uri: null,
  baseSpec: defaultSpec,
  query: defaultQuery,
  title: 'Example Bar Chart',
  description: 'An example chart that looks up the frequency for each class in the knowledge graph.',
  depiction: null,
}

const chartType = 'http://semanticscience.org/resource/Chart'

const foafDepictionUri = 'http://xmlns.com/foaf/0.1/depiction'
const hasContentUri = 'http://vocab.rpi.edu/whyis/hasContent'

const chartFieldPredicates = {
  baseSpec: 'http://semanticscience.org/resource/hasValue',
  query: 'http://schema.org/query',
  title: 'http://purl.org/dc/terms/title',
  description: 'http://purl.org/dc/terms/description',
  dataset: 'http://www.w3.org/ns/prov#used',
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
  const chartLd =  {
    '@id': chart.uri,
    '@type': [chartType],
    [foafDepictionUri]: {
      '@id': `${chart.uri}_depiction`,
      [hasContentUri]: chart.depiction
    }
  }
  Object.entries(chart)
    .filter(([field, value]) => chartFieldPredicates[field])
    .forEach(([field, value]) => chartLd[chartFieldPredicates[field]] = [{ '@value': value }])
  return chartLd
}

function extractChart (chartLd) {
  const chart = {uri: chartLd['@id']}

  if (chartLd[foafDepictionUri]) {
    chart.depiction = chartLd[foafDepictionUri][0]['@id']
  }

  Object.entries(chartFieldPredicates)
    .filter(([field, uri]) => uri in chartLd)
    .forEach(([field, uri]) => chart[field] = chartLd[uri][0]['@value'])

  chart.baseSpec = JSON.parse(chart.baseSpec)
  return chart
}

function getDefaultChart () {
  return Object.assign({}, defaultChart)
}

/**
 * Copies the given chart except for the id field, which is generated from scratch
 * also the depiction is removed
 */
function copyChart(sourceChart) {
  // Shallow copy is OK for the current chart structure
  const newChart = Object.assign({}, sourceChart)
  newChart.uri = generateChartId()
  delete newChart.depiction
  return newChart
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
  PREFIX foaf: <http://xmlns.com/foaf/0.1/>
  PREFIX prov: <http://www.w3.org/ns/prov#>
  PREFIX dcat: <http://www.w3.org/ns/dcat#>
  SELECT DISTINCT ?uri ?downloadUrl ?title ?description ?query ?dataset ?baseSpec ?depiction
  WHERE {
    ?uri a sio:Chart .
    OPTIONAL { ?uri dcterms:title ?title } .
    OPTIONAL { ?uri dcterms:description ?description } .
    OPTIONAL { ?uri schema:query ?query } .
    OPTIONAL { ?uri prov:used ?dataset}
    OPTIONAL { ?uri sio:hasValue ?baseSpec } .
    OPTIONAL { ?uri foaf:depiction ?depiction } .
    OPTIONAL { ?uri dcat:downloadURL ?downloadUrl } .
  }
  `

async function getCharts () {
  const {results} = await querySparql(chartQuery)
  const charts = []
  for (let row of results.bindings) {
    charts.push(await readChartSparqlRow(row))
  }
  return charts
}

async function loadChart(chartUri) {
  const singleChartQuery = chartQuery + `\n  VALUES (?uri) { (<${chartUri}>) }`
  const {results} = await querySparql(singleChartQuery)
  const rows = results.bindings
  if (rows.length < 1) {
    throw `No chart found for uri: ${chartUri}`
  }
  return await readChartSparqlRow(rows[0])
}

async function readChartSparqlRow(chartResult) {
  const chart = {}
  Object.entries(chartResult)
    .forEach(([field, value]) => chart[field] = value.value)
  if (chart.baseSpec) {
    chart.baseSpec = JSON.parse(chart.baseSpec)
  } else if (chart.downloadUrl) {
    const {data} = await axios.get(`/about?uri=${chart.uri}`)
    chart.baseSpec = data
  }
  return chart
}

function transformSparqlData (sparqlResults) {
  const data = []
  if (sparqlResults && sparqlResults.hasOwnProperty('results')) {
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

async function loadDatasetResults(datasetUri) {
  if (!/\.csv$/.test(datasetUri)) {
    throw "dataset upload only works with csv right now"
  }
  const parsedData = await (new Promise(resolve => {
    Papa.parse(`/about?uri=${datasetUri}`, {
      download: true,
      complete: results => resolve(results.data)
    })
  }))
  const results = {
    head: {
      vars: parsedData[0]
    },
    results: {
      bindings: parsedData.slice(1).map(row => {
        const binding = {}
        for (let i = 0; i < row.length; i++) {
          binding[parsedData[0][i]] = {
            type: "literal",
            value: row[i]
          }
        }
        return binding
      })
    }
  }
  console.log('PARSED', results)
  return results
}

async function loadData(chart) {
  if (chart.query) {
    return await querySparql(chart.query)
  } else if (chart.dataset) {
    return await loadDatasetResults(chart.dataset)
  }
  console.error("chart has no query or dataset", chart)
  throw "Chart has no query or dataset"
}

function buildChartSpec(chart, sparqlResults) {
  if (!chart.baseSpec) {
    return null
  }
  const spec = JSON.parse(JSON.stringify(chart.baseSpec))
  spec.data = { values: transformSparqlData(sparqlResults) }
  return spec
}

async function loadAndBuildChartSpec(chart) {
  const sparqlResults = await loadData(chart)
  return buildChartSpec(chart, sparqlResults)
}

export {
  getDefaultChart,
  loadChart,
  saveChart,
  copyChart,
  getCharts,
  loadData,
  buildChartSpec,
  loadAndBuildChartSpec,
  transformSparqlData
}
