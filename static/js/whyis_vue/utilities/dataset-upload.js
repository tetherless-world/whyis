
import { listNanopubs, postNewNanopub, describeNanopub, deleteNanopub, lodPrefix } from 'utilities/nanopub'
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
  title: "",
  description: "",
  contactpoint: {
    "@type": "individual",
    cpfirstname: "",
    cplastname: "",
    cpemail: "",
  },
  contributor: [],
  author: [],
  datepub: {
    "@type": "date",
    "@value": "",
  },
  datemod: {
    "@type": "date",
    "@value": "",
  },
  refby: [], 
  distribution:{
    accessURL: null,
  },
  depiction: {
    name: '',
    accessURL: null,
  }
}


const datasetType = 'http://www.w3.org/ns/dcat#Dataset'
//const datasetType = 'http://semanticscience.org/resource/Dataset'

// const foafDepictionUri = 'http://xmlns.com/foaf/0.1/depiction'
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
  contributor: `${dct}contributor`,         
  organization: `${foaf}:Organization`, 
  person: `${foaf}:Person`, 
  onbehalfof:"http://www.w3.org/ns/prov#actedOnBehalfOf",

  datepub: `${dct}issued`,
  datemod: `${dct}modified`,
  date: 'https://www.w3.org/2001/XMLSchema#date',

  refby: `${dct}isReferencedBy`,

  distribution: `${dcat}:distribution`,
  depiction: `${foaf}:depiction`,
  accessURL: `${dcat}:accessURL`,
} 
const datasetPrefix = 'dataset' 

function generateDatasetId (guuid) {
  var datasetId;
  if (arguments.length === 0) { 
    const { v4: uuidv4 } = require('uuid');
    datasetId = uuidv4();
  } else {
    datasetId = guuid;
  }
  // const datasetId = Date.now();  
  return `${lodPrefix}/${datasetPrefix}/${datasetId}`
} 

function buildDatasetLd (dataset) {
  dataset = Object.assign({}, dataset)
  dataset.context = JSON.stringify(dataset.context)
  const datasetLd =  {
    // '@context': defaultContext,
    '@id': dataset.uri,
    '@type': [datasetType],
    // [foafDepictionUri]: {
    //   '@id': `${dataset.uri}_depiction`,
    //   [hasContentUri]: dataset.depiction
    // }
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


function loadChartFromNanopub(nanopubUri, datasetUri) {
  return describeNanopub(nanopubUri)
    .then((describeData) => {
      const assertion_id = `${nanopubUri}_assertion`
      for (let graph of describeData) {
        if (graph['@id'] === assertion_id) {
          for (let resource of graph['@graph']) {
            if (resource['@id'] === datasetUri) {
              return extractChart(resource)
            }
          }
        }
      }
    })
}

function loadDataset (datasetUri) {
  return listNanopubs(datasetUri)
    .then(nanopubs => {
      if (nanopubs.length > 0) {
        const nanopubUri = nanopubs[0].np
        return loadChartFromNanopub(nanopubUri, datasetUri)
      }
    })
}


function extractChart (chartLd) {
  const chart = Object.assign({}, defaultDataset)

  Object.entries(defaultDataset)
    .forEach(([field]) => {
      // let value = "";
      let uri = datasetFieldUris[field];
      var val = chartLd[uri];
      console.log(val)
      if ((uri in chartLd) && (typeof val !== `undefined`) ){
        console.log(val[0])
        if (typeof val[0]['@value'] !== `undefined`){
          chart[field] = chartLd[uri][0]['@value']
        }  
      }
      // chart[field] = value
    })
    
  return chart
}


async function saveDataset (dataset, guuid) {
  let deletePromise = Promise.resolve()
  if (dataset.uri) {
    deletePromise = deleteDataset(dataset.uri)
  } else if (arguments.length === 1){
    dataset.uri = generateDatasetId()
  } else {
    dataset.uri = generateDatasetId(guuid)
  } 
  const datasetLd = buildDatasetLd(dataset) 
  await deletePromise
  try{
    return postNewNanopub(datasetLd, defaultContext)
  } catch(err){
    return alert(err)
  }
  
}

function deleteDataset (datasetUri) { 
  return listNanopubs(datasetUri)
    .then(nanopubs => Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np))))
}

export { getDefaultDataset, loadDataset, saveDataset }
