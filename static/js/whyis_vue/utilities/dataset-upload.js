
import { listNanopubs, postNewNanopub, deleteNanopub, lodPrefix } from 'utilities/nanopub'
import { goToView } from 'utilities/views'

const defaultSpec = { 
  //not sure what to put here for datasets
}

const defaultDataset = {
  baseSpec: defaultSpec,
  title: 'Example Dataset',
  description: 'An example dataset.'
}


const datasetType = 'http://www.w3.org/ns/dcat#Dataset'
//const datasetType = 'http://semanticscience.org/resource/Dataset'

const foafDepictionUri = 'http://xmlns.com/foaf/0.1/depiction'
const hasContentUri = 'http://vocab.rpi.edu/whyis/hasContent'

const datasetFieldUris = {
  baseSpec: 'http://semanticscience.org/resource/hasValue',
  query: 'http://schema.org/query',
  title: 'http://www.w3.org/ns/dcat#/title',
  contactPoint: 'http://www.w3.org/ns/dcat#/title',
  author: 'http://purl.org/dc/terms/creator',
  organization: 'http://purl.org/dc/terms/contributor',
  description: 'http://purl.org/dc/terms/description',
  dateModified: 'http://purl.org/dc/terms/modified',
}


const datasetPrefix = 'ds'
const datasetLen = 16

function generateDatasetId () {
  const intArr = new Uint8Array(datasetLen / 2)
  window.crypto.getRandomValues(intArr)
  const datasetId = Array.from(intArr, (dec) => ('0' + dec.toString(16)).substr(-2)).join('')

  return `${lodPrefix}/${datasetPrefix}/${datasetId}`
}

function buildDatasetLd (dataset) {
  dataset = Object.assign({}, dataset)
  dataset.baseSpec = JSON.stringify(dataset.baseSpec)
  const datasetLd =  {
    '@id': dataset.uri,
    '@type': [datasetType],
    [foafDepictionUri]: {
      '@id': `${dataset.uri}_depiction`,
      [hasContentUri]: dataset.depiction
    }
  }

  Object.entries(dataset)
    .filter(([field, value]) => datasetFieldUris[field])
    .forEach(([field, value]) => datasetLd[datasetFieldUris[field]] = [{ '@value': value }])
  return datasetLd
}

function getDefaultDataset () {
  return Object.assign({}, defaultDataset)
}

function saveDataset (dataset) {
  let deletePromise = Promise.resolve()
  if (dataset.uri) {
    deletePromise = deleteDataset(dataset.uri)
  } else {
    dataset.uri = generateDatasetId()
  }
  const datasetLd = buildDatasetLd(dataset)
  return deletePromise
    .then(() => postNewNanopub(datasetLd))
}

function deleteDataset (datasetUri) {
  console.log('Deleting dataset', datasetUri)
  return listNanopubs(datasetUri)
    .then(nanopubs => Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np))))
}

export { getDefaultDataset, saveDataset }
