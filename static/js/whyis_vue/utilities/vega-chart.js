
import { listNanopubs, getLocalNanopub, describeNanopub, postNewNanopub, lodPrefix } from './nanopub'

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
    .then(extractChart)
}

function loadNanopubChart (chartUri) {
  return describeNanopub(chartUri)
    .then((response) => response[0]['@graph'][0])
    .then(extractChart)
}

function saveChart (chart) {
  const chartLd = buildChartLd(chart)
  return postNewNanopub(chartLd)
    .then((resp) => console.log(resp))
}

export { loadDefaultChart, loadNanopubChart, saveChart }
