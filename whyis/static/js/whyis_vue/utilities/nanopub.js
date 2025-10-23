/**
 * Nanopublication utilities for managing scientific claims and assertions.
 * Provides functions for creating, reading, updating, and deleting nanopublications
 * in the Whyis knowledge graph.
 * 
 * @module nanopub
 */

import axios from 'axios'

/**
 * Gets the base URL for nanopublication endpoints (lazy evaluation to avoid build-time errors)
 * @returns {string} The nanopub base URL
 */
const nanopubBaseUrl = () => `${window.ROOT_URL}pub`

/**
 * Gets the Linked Open Data prefix used for generating URIs (lazy evaluation to avoid build-time errors)
 * @returns {string} The LOD prefix from global scope
 */
const lodPrefix = () => window.LOD_PREFIX

/**
 * Constructs a URL for a specific nanopublication ID
 * @param {string} id - The nanopublication ID
 * @returns {string} The complete nanopublication URL
 */
function getNanopubUrl (id) {
  return `${nanopubBaseUrl()}/${id}`
}

/**
 * Constructs an 'about' URL for a given URI
 * @param {string} uri - The URI to construct an about URL for
 * @returns {string} The about URL
 */
function getAboutUrl(uri) {
  return `${window.ROOT_URL}about?uri=${uri}`
}

/**
 * Fetches detailed description data for a nanopublication
 * @param {string} uri - The URI of the nanopublication to describe
 * @returns {Promise<Object>} Promise that resolves to the nanopublication description data
 * @example
 * const nanopubData = await describeNanopub('http://example.com/nanopub/123');
 */
function describeNanopub (uri) {
  console.debug(`loading nanopub ${uri}`)
  return axios.get(`${window.ROOT_URL}about?view=describe&uri=${encodeURIComponent(uri)}`)
    .then((response) => {
      console.debug('received nanopub data for uri:', uri, response)
      return response.data
    })
}

/**
 * Retrieves a list of nanopublications associated with a given URI
 * @param {string} uri - The URI to list nanopublications for
 * @returns {Promise<Array>} Promise that resolves to an array of nanopublication objects
 * @example
 * const nanopubs = await listNanopubs('http://example.com/resource');
 */
function listNanopubs (uri) {
  return axios.get(`${window.ROOT_URL}about?view=nanopublications&uri=${encodeURIComponent(uri)}`)
    .then(response => {
      console.debug('list nanopub response', response)
      return response.data
    })
}

/**
 * Retrieves a local nanopublication by its ID
 * @param {string} id - The nanopublication ID
 * @returns {Promise<Object>} Promise that resolves to the nanopublication data
 */
function getLocalNanopub (id) {
  console.debug(`loading nanopub ${id}`)
  const url = getNanopubUrl(id)
  return axios.get(url)
    .then((response) => {
      console.debug('received nanopub data for url:', url, response)
      return response
    })
}

/**
 * Generates a unique nanopublication ID using random characters
 * @returns {string} A unique nanopublication ID
 */
function makeNanopubId() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return Math.random().toString(36).substr(2, 10);
}

/**
 * Creates a nanopublication skeleton structure with required components
 * @returns {Object} A complete nanopublication skeleton with assertion, provenance, and publication info
 * @example
 * const skeleton = getNanopubSkeleton();
 * // Returns a structured nanopublication template ready for data insertion
 */
function getNanopubSkeleton () {
  //doot
  const prefix = lodPrefix()
  const npId = `${prefix}/pub/${makeNanopubId()}` //make sure this change doesn't break other things
  return {
    "@context": {
      "@vocab": prefix+'/',
      "@base": prefix+'/',
      "np" : "http://www.nanopub.org/nschema#",
    },
    "@id": npId,
    "@graph" : {
      "@id" : npId,
      "@type": "np:Nanopublication",
      "np:hasAssertion" : {
        "@id" : npId + "_assertion",
        "@type" : "np:Assertion",
        "@graph" : []
      },
      "np:hasProvenance" : {
        "@id" : npId + "_provenance",
        "@type" : "np:Provenance",
        "@graph" : {
          "@id": npId + "_assertion"
        }
      },
      "np:hasPublicationInfo" : {
        "@id" : npId + "_pubinfo",
        "@type" : "np:PublicationInfo",
        "@graph" : {
            "@id": npId,
        }
      }
    }
  }
}

/**
 * Posts a new nanopublication to the knowledge graph
 * @param {Object} pubData - The publication data to include in the assertion
 * @param {Object} [context] - Optional JSON-LD context to merge with the default context
 * @returns {Promise<Object>} Promise that resolves to the server response
 * @example
 * const result = await postNewNanopub({
 *   '@id': 'http://example.com/claim',
 *   '@type': 'schema:Article',
 *   'schema:name': 'Example Claim'
 * });
 */
function postNewNanopub (pubData, context) {
  const nanopub = getNanopubSkeleton()
  if (context) {
    nanopub['@context'] = {...nanopub['@context'], ...context}
  }
  nanopub['@graph']['np:hasAssertion']['@graph'].push(pubData)
  const request = {
    method: 'post',
    url: nanopubBaseUrl(),
    data: nanopub,
    headers: {
      'Content-Type': 'application/ld+json'
    }
  }
  // console.log(request)
  return axios(request)
}

/**
 * Deletes a nanopublication from the knowledge graph
 * @param {string} uri - The URI of the nanopublication to delete
 * @returns {Promise<Object>} Promise that resolves to the delete response
 * @example
 * await deleteNanopub('http://example.com/nanopub/123');
 */
function deleteNanopub (uri) {
  console.debug('deleting nanopub', uri)
  return axios.delete(getAboutUrl(uri))
    .then(resp => {
      console.debug('delete nanopub response', uri, resp)
      return resp
    })
}

export {
  listNanopubs,
  getLocalNanopub,
  describeNanopub,
  postNewNanopub,
  deleteNanopub,
  lodPrefix
}
