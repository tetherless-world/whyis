
import { listNanopubs, postNewNanopub, deleteNanopub, lodPrefix } from 'utilities/nanopub'
import { goToView } from 'utilities/views'

const defaultContext= { 
  "dcat": "http://w3.org/ns/dcat#",
  "dct": "http://purl.org/dc/terms/",
  "vcard": "http://www.w3.org/2006/vcard/ns#",
  "foaf": "http://xmlns.com/foaf/0.1/",
  
  "title": "dct:title",
  "description": "dct:description",
  
  "contactpoint": "dcat:contactpoint", 
  "cpemail": "vcard:email",
  "cpfirstname": "vcard:given-name",
  "cplastname": "vcard:family-name",
  "individual": "vcard:individual",
  
  "name": "foaf:name",
  "contributor": "dct:contributor",         
  "organization": "foaf:Organization",
  "author": "dct:creator", 
  "person": "foaf:Person",
  "lastname":"foaf:lastname",
  "firstname":"foaf:firstname",
  "onbehalfof":"http://www.w3.org/ns/prov#actedOnBehalfOf",

  "datepub": "dct:issued",
  "datemod": "dct:modified",
  
  "refby":"dct:isReferencedBy",
  "repimage":"foaf:depiction",
  "distribution": "dcat:distribution"
}

const defaultDataset = {
  "@context": defaultContext,
  title: 'Example Dataset',
  description: 'An example dataset.'
}


const datasetType = 'http://www.w3.org/ns/dcat#Dataset'
//const datasetType = 'http://semanticscience.org/resource/Dataset'

const foafDepictionUri = 'http://xmlns.com/foaf/0.1/depiction'
const hasContentUri = 'http://vocab.rpi.edu/whyis/hasContent'

const dcat = "http://w3.org/ns/dcat#"
const dct = "http://purl.org/dc/terms/"
const vcard = "http://www.w3.org/2006/vcard/ns#"
const foaf = "http://xmlns.com/foaf/0.1/"

const datasetFieldUris = {
  baseSpec: 'http://semanticscience.org/resource/hasValue', 
  title: `${dcat}title`,
  description: `${dct}description`, 

  contactpoint: `${dcat}contactpoint`,
  cpemail: `${vcard}email`,
  cpfirstname: `${vcard}given-name`,
  cplastname: `${vcard}family-name`,
  individual: `${vcard}individual`,

  author: `${dct}creator`,
  name: `${foaf}:name`,
  contributor: `${dct}:contributor`,         
  organization: `${foaf}:Organization`, 
  person: `${foaf}:Person`, 
  onbehalfof:"http://www.w3.org/ns/prov#actedOnBehalfOf",

  datepub: `${dct}issued`,
  datemod: `${dct}modified`,
  date: 'https://www.w3.org/2001/XMLSchema#date',

  refby: `${dct}isReferencedBy`,
} 
const datasetPrefix = 'ds' 

function generateDatasetId () {
  const datasetId = Date.now();  
  return `${lodPrefix}/${datasetPrefix}/${datasetId}`
}

function buildDatasetLd (dataset) {
  dataset = Object.assign({}, dataset)
  dataset.context = JSON.stringify(dataset.context)
  const datasetLd =  {
    // '@context': defaultContext,
    '@id': dataset.uri,
    '@type': [datasetType],
    [foafDepictionUri]: {
      '@id': `${dataset.uri}_depiction`,
      [hasContentUri]: dataset.depiction
    }
  }

  Object.entries(dataset)
    .filter(([field, value]) => datasetFieldUris[field])
    .forEach(([field, value]) => {  
      var ldValues = {};
      if ((value!=="")&&(value!==null)){ 
        ldValues = recursiveFieldSetter([field, value]);
        datasetLd[datasetFieldUris[field]] = [ldValues];
      }
    })
  return datasetLd
}

function recursiveFieldSetter ([field, value]) { 
  var fieldDict = {} 
  for (var val in value) {  
    if (Array.isArray(value)){
      fieldDict[val] = recursiveFieldSetter([field, value[val]])
    } 
    else if ((val === '@type') || (val === '@value')){ 
      fieldDict[val] = value[val];
      if (datasetFieldUris.hasOwnProperty(value[val])){
        fieldDict[val] = datasetFieldUris[value[val]];
      }
    }
    else if (datasetFieldUris.hasOwnProperty(val)){ 
      fieldDict[datasetFieldUris[val]] = recursiveFieldSetter([datasetFieldUris[val], value[val]]);
    } else {
      fieldDict['@value'] = value;
    }
  }
  return fieldDict
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
  console.log(dataset.uri);
  const datasetLd = buildDatasetLd(dataset)
  console.log(datasetLd);
  return deletePromise
    .then(() => console.log('Reached the end'))
    // .then(() => postNewNanopub(datasetLd))
}

function deleteDataset (datasetUri) { 
  return listNanopubs(datasetUri)
    .then(nanopubs => Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np))))
}

export { getDefaultDataset, saveDataset }
