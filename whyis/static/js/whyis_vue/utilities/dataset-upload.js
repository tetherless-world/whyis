/**
 * Dataset upload and management utilities for handling research datasets.
 * Provides functions for creating, loading, saving, and managing datasets
 * with support for metadata, distributions, and linked data formats.
 * 
 * @module dataset-upload
 */

import axios from 'axios'
import { listNanopubs, postNewNanopub, describeNanopub, deleteNanopub, lodPrefix } from './nanopub'

// Simple UUID v4 generator
function uuidv4() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

/**
 * Default dataset structure with all required fields
 * @constant {Object} defaultDataset
 * @property {string} title - Dataset title
 * @property {string} description - Dataset description
 * @property {Object} contactpoint - Contact person information
 * @property {Array} contributor - List of contributors
 * @property {Array} author - List of authors
 * @property {Object} datepub - Publication date
 * @property {Object} datemod - Modification date
 * @property {Array} refby - Referenced by resources
 * @property {Object} distribution - Data distribution information
 * @property {Object} depiction - Visual representation
 */
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

/**
 * RDF type URI for datasets
 * @constant {string} datasetType
 */
const datasetType = 'http://www.w3.org/ns/dcat#Dataset'

// Namespace prefixes for RDF vocabularies
const dcat = "http://w3.org/ns/dcat#"
const dct = "http://purl.org/dc/terms/"
const vcard = "http://www.w3.org/2006/vcard/ns#"
const foaf = "http://xmlns.com/foaf/0.1/"

/**
 * Mapping of dataset fields to their corresponding RDF URIs
 * @constant {Object} datasetFieldUris
 */
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

/**
 * Prefix used for generating dataset URIs
 * @constant {string} datasetPrefix
 */
const datasetPrefix = 'dataset'

/**
 * Generates a unique dataset ID, either new UUID or reuses existing one
 * @param {string} [guuid] - Optional existing UUID to reuse
 * @returns {string} Complete dataset URI
 * @example
 * const newId = generateDatasetId(); // Generates new UUID
 * const existingId = generateDatasetId('existing-uuid'); // Reuses UUID
 */
function generateDatasetId (guuid) {
  var datasetId;
  if (arguments.length === 0) {
    datasetId = uuidv4();
  } else {
    datasetId = guuid;
  }
  return `${lodPrefix()}/${datasetPrefix}/${datasetId}`
}

/**
 * Converts a dataset object to JSON-LD format for storage
 * @param {Object} dataset - The dataset object to convert
 * @returns {Object} JSON-LD representation of the dataset
 */
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

/**
 * Recursively checks if a value is empty (null, undefined, empty string, empty array, or empty object)
 * @param {*} value - The value to check
 * @returns {boolean} True if the value is considered empty
 */
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

/**
 * Helper function for recursively converting field values to JSON-LD format
 * @param {Array} fieldValue - Array containing [field, value] pair
 * @returns {Object|Array} JSON-LD formatted field value
 */
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

/**
 * Returns a blank dataset object with default structure
 * @returns {Object} A copy of the default dataset template
 */
function getDefaultDataset () {
  return Object.assign({}, defaultDataset)
}

/**
 * Loads dataset data from a specific nanopublication
 * @param {string} nanopubUri - URI of the nanopublication containing the dataset
 * @param {string} datasetUri - URI of the dataset to load
 * @returns {Promise<Object>} Promise that resolves to the extracted dataset object
 */
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

/**
 * Loads a dataset by finding and loading its most recent nanopublication
 * @param {string} datasetUri - URI of the dataset to load
 * @returns {Promise<Object>} Promise that resolves to the dataset object
 */
function loadDataset (datasetUri) {
  return listNanopubs(datasetUri)
    .then(nanopubs => {
      if (nanopubs.length > 0) {
        const nanopubUri = nanopubs[0].np
        return loadDatasetFromNanopub(nanopubUri, datasetUri)
      }
    })
}

/**
 * Extracts dataset information from JSON-LD format into application format
 * @param {Object} datasetLd - JSON-LD representation of the dataset
 * @returns {Object} Dataset object in application format
 */
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

/**
 * Saves a dataset to the knowledge graph as a nanopublication
 * @param {Object} dataset - The dataset object to save
 * @param {string} [guuid] - Optional UUID to use for the dataset
 * @returns {Promise<Object>} Promise that resolves to the save response
 * @example
 * const result = await saveDataset({
 *   title: 'My Dataset',
 *   description: 'A sample dataset',
 *   author: ['John Doe']
 * });
 */
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

/**
 * Deletes all nanopublications associated with a dataset
 * @param {string} datasetUri - URI of the dataset to delete
 * @returns {Promise} Promise that resolves when deletion is complete
 */
function deleteDataset (datasetUri) {
  return listNanopubs(datasetUri)
    .then(nanopubs => {
      console.log("in delete")
      console.log(nanopubs.np)
      Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np)))
    }
    )
}

/**
 * Saves file distributions for a dataset
 * @param {FileList} fileList - List of files to upload as distributions
 * @param {string} id - Dataset ID to associate files with
 * @returns {Promise} Promise that resolves when files are uploaded
 */
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
        '@id': `${lodPrefix()}/dataset/${id}/${fileList[x].name.replace(/ /g, '_')}`,
        'http://www.w3.org/2000/01/rdf-schema#label': fileList[x].label,
      }
    });


  // Where to save the distribution
  const uri = `${lodPrefix()}/dataset/${id}`;
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

/**
 * Saves an image file as a dataset depiction
 * @param {File} file - Image file to upload
 * @param {string} id - Dataset ID to associate the image with
 * @returns {Promise<Array>} Promise that resolves to [uri, baseUrl] of the saved image
 */
async function saveImg(file, id){
  // Where to save the image
  const uri = `${lodPrefix()}/dataset/${id}/depiction`;
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

/**
 * Fetches DOI (Digital Object Identifier) metadata
 * @param {string} doi - The DOI to fetch metadata for
 * @returns {Promise<Object>} Promise that resolves to DOI metadata
 */
async function getDoi(doi){
  const response = await axios.get(`/doi/${doi}?view=describe`, {
    headers: {
      'Accept': 'application/json',
    }
  });
  return response
}

/**
 * Retrieves detailed author information by author ID
 * @param {string} authorId - URI of the author to fetch information for
 * @returns {Promise<Object>} Promise that resolves to author information
 */
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
