
/**
 * Vega-Lite chart management utilities for creating, saving, and loading interactive visualizations.
 * Provides functions for managing chart specifications, SPARQL data integration, and chart persistence.
 * 
 * @module vega-chart
 */

import { literal, namedNode } from '@rdfjs/data-model'
import { fromRdf } from 'rdf-literal'
import axios from 'axios'

import { listNanopubs, getLocalNanopub, describeNanopub, postNewNanopub, deleteNanopub, lodPrefix } from './nanopub'
import { querySparql } from './sparql'

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

/**
 * Generates a unique chart identifier using cryptographic random values
 * @returns {string} A unique chart URI with the format lodPrefix/viz/randomId
 */
function generateChartId () {
  const intArr = new Uint8Array(chartIdLen / 2)
  window.crypto.getRandomValues(intArr)
  const chartId = Array.from(intArr, (dec) => ('0' + dec.toString(16)).substr(-2)).join('')

  return `${lodPrefix()}/${chartPrefix}/${chartId}`
}

/**
 * Converts a chart object to JSON-LD format for storage
 * @param {Object} chart - The chart object to convert
 * @returns {Object} JSON-LD representation of the chart
 */
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

/**
 * Extracts chart data from JSON-LD format into application format
 * @param {Object} chartLd - JSON-LD representation of a chart
 * @returns {Object} Chart object in application format with parsed baseSpec
 */
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

/**
 * Returns a default chart template with sample SPARQL query and Vega-Lite specification
 * @returns {Object} Default chart object with query, baseSpec, title, and description
 */

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

/**
 * Saves a chart to the knowledge graph as a nanopublication
 * @param {Object} chart - The chart object to save
 * @returns {Promise<Object>} Promise that resolves to the save response
 * @example
 * const result = await saveChart({
 *   title: 'My Chart',
 *   query: 'SELECT * WHERE { ?s ?p ?o }',
 *   baseSpec: {...vegaLiteSpec}
 * });
 */
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

/**
 * Deletes all nanopublications associated with a chart
 * @param {string} chartUri - URI of the chart to delete
 * @returns {Promise} Promise that resolves when deletion is complete
 */
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
    { ?uri a sio:Chart . } UNION { ?uri a sio:SIO_000904 .}
    OPTIONAL { ?uri dcterms:title ?title } .
    OPTIONAL { ?uri dcterms:description ?description } .
    OPTIONAL { ?uri schema:query ?query } .
    OPTIONAL { ?uri prov:used ?dataset}
    OPTIONAL { ?uri sio:hasValue|sio:SIO_000300 ?baseSpec } .
    OPTIONAL { ?uri foaf:depiction ?depiction } .
    OPTIONAL { ?uri dcat:downloadURL ?downloadUrl } .
  }
  `

/**
 * Retrieves all charts from the knowledge graph
 * @returns {Promise<Array>} Promise that resolves to an array of chart objects
 * @example
 * const allCharts = await getCharts();
 * console.log(allCharts.length, 'charts found');
 */
async function getCharts () {
  const {results} = await querySparql(chartQuery)
  const charts = []
  for (let row of results.bindings) {
    charts.push(await readChartSparqlRow(row))
  }
  return charts
}

/**
 * Loads a specific chart by its URI
 * @param {string} chartUri - The URI of the chart to load
 * @returns {Promise<Object>} Promise that resolves to the chart object
 * @throws {string} If no chart is found for the given URI
 * @example
 * const chart = await loadChart('http://example.com/chart/123');
 */
async function loadChart(chartUri) {
  const singleChartQuery = chartQuery + `\n  VALUES (?uri) { (<${chartUri}>) }`
  const {results} = await querySparql(singleChartQuery)
  const rows = results.bindings
  if (rows.length < 1) {
    throw `No chart found for uri: ${chartUri}`
  }
  return await readChartSparqlRow(rows[0])
}

/**
 * Processes a SPARQL result row into a chart object
 * @param {Object} chartResult - Raw SPARQL result row
 * @returns {Promise<Object>} Promise that resolves to a formatted chart object
 */
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

/**
 * Transforms SPARQL result bindings into a format suitable for Vega-Lite visualization
 * @param {Object} sparqlResults - SPARQL query results with bindings
 * @returns {Array} Array of data objects with proper type conversion
 * @example
 * const data = transformSparqlData(sparqlResults);
 * // Returns array of objects with converted literal types
 */
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

/**
 * Combines a Vega-Lite specification with SPARQL results to create a complete chart spec
 * @param {Object} baseSpec - Base Vega-Lite specification
 * @param {Object} sparqlResults - SPARQL query results to embed in the chart
 * @returns {Object|null} Complete Vega-Lite specification with data, or null if no baseSpec
 * @example
 * const spec = buildSparqlSpec(chartSpec, sparqlResults);
 * // Returns Vega-Lite spec with embedded data from SPARQL
 */
function buildSparqlSpec (baseSpec, sparqlResults) {
  if (!baseSpec) {
    return null
  }
  const spec = Object.assign({}, baseSpec)
  if (spec.data != null) {
    if (spec.datasets == null) {
      spec.datasets = {}
    }
    spec.datasets['results'] = transformSparqlData(sparqlResults)
  } else {
    spec.data = { values: transformSparqlData(sparqlResults) }
  }
  return spec
}

export { getDefaultChart, loadChart, saveChart, copyChart, getCharts, buildSparqlSpec, transformSparqlData}
