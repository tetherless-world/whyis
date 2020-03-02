
import { listNanopubs, getLocalNanopub, describeNanopub, postNewNanopub, deleteNanopub, lodPrefix } from './nanopub'

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
  if (chartLd['@id'] !== defaultChartUri) {
    chart.uri = chartLd['@id']
  }

  return chart
}

function loadDefaultChart () {
  return describeNanopub(defaultChartUri)
    .then((data) => data.filter((pub) => pub['@id'] === defaultChartUri)[0])
    .then(extractChart)
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

export { loadDefaultChart, loadChart, saveChart }
