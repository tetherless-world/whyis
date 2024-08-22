import uuidv4 from 'uuid'

import { listNanopubs, postNewNanopub, describeNanopub, deleteNanopub, lodPrefix } from './nanopub'
import axios from 'axios'


const defaultDataset = {
  title: "",
  description: "",
  contactpoint: {
    "@type": "individual",
    "@id": null,
    name:"",
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

const dcat = "http://w3.org/ns/dcat#"
const dct = "http://purl.org/dc/terms/"
const vcard = "http://www.w3.org/2006/vcard/ns#"
const foaf = "http://xmlns.com/foaf/0.1/"

const datasetFieldUris = {
  baseSpec: 'http://semanticscience.org/resource/hasValue',
  title: `${dct}title`,
  description: `${dct}description`,

  contactpoint: `${dcat}contactpoint`,
  cpemail: `${vcard}email`,
  cpfirstname: `${vcard}given-name`,
  cplastname: `${vcard}family-name`,
  individual: `${vcard}individual`,

  author: `${dct}creator`,
  name: `${foaf}name`,
  contributor: `${dct}contributor`,
  organization: `${foaf}Organization`,
  person: `${foaf}Person`,
  onbehalfof:"http://www.w3.org/ns/prov#actedOnBehalfOf",
  specializationOf:"http://www.w3.org/ns/prov#specializationOf",

  datepub: `${dct}issued`,
  datemod: `${dct}modified`,
  date: 'https://www.w3.org/2001/XMLSchema#date',

  refby: `${dct}isReferencedBy`,

  // distribution: `${dcat}distribution`,
  depiction: `${foaf}depiction`,
  hasContent: 'http://vocab.rpi.edu/whyis/hasContent',
  accessURL: `${dcat}accessURL`,
}

const datasetPrefix = 'dataset'

// Generate a randum uuid, or use current if exists
function generateDatasetId (guuid) {
  var datasetId;
  if (arguments.length === 0) {
    datasetId = uuidv4();
  } else {
    datasetId = guuid;
  }
  return `${lodPrefix}/${datasetPrefix}/${datasetId}`
}

function buildDatasetLd (dataset) {
  dataset = Object.assign({}, dataset)
  dataset.context = JSON.stringify(dataset.context)
  const datasetLd =  {
    '@id': dataset.uri,
    '@type': [],
  }

    if (dataset['@type'] != null) {
	datasetLd['@type'].push(dataset['@type'])
    }

  Object.entries(dataset)
    // filter out the ones that aren't in our allowed fields
    .filter(([field, value]) => datasetFieldUris[field])
    .forEach(([field, value]) => {
      // make a new dictionary
      var ldValues = {};
      console.log(field)
      // If the field has a value
      if (!isEmpty(value)){
        ldValues = recursiveFieldSetter([field, value]);
        datasetLd[datasetFieldUris[field]] = [ldValues];
      }
    })
  return datasetLd
}

// Recursively check if a value is empty
function isEmpty(value) {
  // Base case
  if ((value==="")||(value===null)||(value===[])||(value==="undefined")){
    return true
  } else if (Array.isArray(value)) {
    // Is empty if array has length 0
    let arrayEmpty = (value.length === 0);
    for (var val in value) {
      // if any entry in the array is empty, it's empty
      arrayEmpty = arrayEmpty || isEmpty(value[val]);
    }
    return arrayEmpty;
  } else if (typeof(value) === 'object') {
    let objEmpty = false;
    for (var property in value) {
      // if any attribute of the object is empty, it's empty
      objEmpty = objEmpty || isEmpty(value[property]);
    }
    return objEmpty
  }
  return false
}

// Helper for assigning values into JSON-LD format
function recursiveFieldSetter ([field, value]) {

  // If the value is also an array, recur through the value
  if (Array.isArray(value)){
    var fieldArray = []
    for (var val in value) {
      // console.log(val)
      // console.log(value[val])
      fieldArray.push( recursiveFieldSetter([field, value[val]]) );
    }
    return fieldArray
  }
  else{
    var fieldDict = {}
    // Fields may have multiple values, so loop through all
    for (var val in value) {

      // type, value and id aren't in datasetFieldURIs dictionary
      // but they are valid keys, so set the value to their value
      if ((val === '@type') || (val === '@value') || (val === '@id')){
        fieldDict[val] = value[val];
        // but if the value of val is an allowed field, use the field's value
        // e.g., type = organization, and organization -> foaf:Organization
        if (datasetFieldUris.hasOwnProperty(value[val])){
          fieldDict[val] = datasetFieldUris[value[val]];
        }
      }
      // Recursive case (val is an allowed field)
      else if (datasetFieldUris.hasOwnProperty(val)){
        fieldDict[datasetFieldUris[val]] = recursiveFieldSetter([datasetFieldUris[val], value[val]]);
      }
      // Base case
      else {
        fieldDict['@value'] = value;
      }
    }
    return fieldDict

  }
}

// Blank dataset
function getDefaultDataset () {
  return Object.assign({}, defaultDataset)
}

// Load for editing
function loadDatasetFromNanopub(nanopubUri, datasetUri) {
  return describeNanopub(nanopubUri)
    .then((describeData) => {
      const assertion_id = `${nanopubUri}_assertion`
      for (let graph of describeData) {
        if (graph['@id'] === assertion_id) {
          for (let resource of graph['@graph']) {
            if (resource['@id'] === datasetUri) {
              return extractDataset(resource)
            }
          }
        }
      }
    })
}

// Load for editing
function loadDataset (datasetUri) {
  return listNanopubs(datasetUri)
    .then(nanopubs => {
      if (nanopubs.length > 0) {
        const nanopubUri = nanopubs[0].np
        return loadDatasetFromNanopub(nanopubUri, datasetUri)
      }
    })
}

// Extract information from dataset in JSONLD format
// TODO: re-write to assign all values in correct format
function extractDataset (datasetLd) {
  const dataset = Object.assign({}, defaultDataset)

  Object.entries(defaultDataset)
    .forEach(([field]) => {
      // let value = "";
      let uri = datasetFieldUris[field];
      var val = datasetLd[uri];
      console.log(val)
      if ((uri in datasetLd) && (typeof val !== `undefined`) ){
        console.log(val[0])
        if (typeof val[0]['@value'] !== `undefined`){
          dataset[field] = datasetLd[uri][0]['@value']
        }
      }
      // dataset[field] = value
    })

  return dataset
}


async function saveDataset (dataset, guuid) {
  let p = Promise.resolve()
  if (dataset.uri) {
    p = deleteDataset(dataset.uri)
  } else if (arguments.length === 1){
    dataset.uri = generateDatasetId()
  } else {
    dataset.uri = generateDatasetId(guuid)
  }
  const datasetLd = buildDatasetLd(dataset)
  await p
  try{
    return postNewNanopub(datasetLd)
  } catch(err){
    return alert(err)
  }

}

function deleteDataset (datasetUri) {
  return listNanopubs(datasetUri)
    .then(nanopubs => {
      console.log("in delete")
      console.log(nanopubs.np)
      Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np)))
    }
    )
}

async function saveDistribution(fileList, id){
  let distrData = new FormData();
  let distrLDs = Array(fileList.length);
  // Specify is a dataset so handles multiple files
  distrData.append('upload_type', 'http://www.w3.org/ns/dcat#Dataset')

  // append the files to FormData
  Array
    .from(Array(fileList.length).keys())
    .map(x => {
      distrData.append(fileList[x].label, fileList[x]);
      distrLDs[x] = {
        '@id': `${lodPrefix}/dataset/${id}/${fileList[x].name.replace(/ /g, '_')}`,
        'http://www.w3.org/2000/01/rdf-schema#label': fileList[x].label,
      }
    });


  // Where to save the distribution
  const uri = `${lodPrefix}/dataset/${id}`;
  const baseUrl = `${window.location.origin}/about?uri=${uri}`;
  axios.post( baseUrl,
      distrData,
      {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
      }
  )
  Array
    .from(Array(fileList.length).keys())
    .map(x => {
      if(distrLDs[x]['http://www.w3.org/2000/01/rdf-schema#label'] != ''){
        postNewNanopub(distrLDs[x])
      }
  });

}

async function saveImg(file, id){
  // Where to save the image
  const uri = `${lodPrefix}/dataset/${id}/depiction`;
  const baseUrl = `${window.location.origin}/about?uri=${uri}`

  let form = new FormData();
  form.append('upload_type', 'http://purl.org/net/provenance/ns#File')
  form.append('depiction', file)

  var data = {
    '@id': uri,
    'file': form,
  }

  await fetch(baseUrl, {
    method: 'POST',
    body: data,
    headers: {
        Accept: 'application/json',
        'Content-Type': 'multipart/form-data',
    },
  })
  return [uri, baseUrl];
}

async function getDoi(doi){
  const response = await axios.get(`/doi/${doi}?view=describe`, {
    headers: {
      'Accept': 'application/json',
    }
  });
  return response
}

async function getDatasetAuthor(authorId){
  // Use describe view on listed authors
  const response = await axios.get(`/about?uri=${authorId}&view=describe`, {
    headers: {
      'Accept': 'application/json',
    }
  })
  var doiAuth = response.data
  if ('@graph' in response.data){
    for (var entry in response.data['@graph']){
      if (response.data['@graph'][entry]['@id'] === authorId){
        doiAuth = response.data['@graph'][entry]
      }
    }
  }
  return doiAuth
}


export { getDefaultDataset, loadDataset, saveDataset, deleteDataset, saveDistribution, saveImg, getDoi, getDatasetAuthor}
