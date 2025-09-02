/**
 * SPARQL query utilities for interacting with the Whyis knowledge graph.
 * Provides functions to execute SPARQL queries against the RDF triple store.
 * 
 * @module sparql
 */

import axios from 'axios'

/**
 * SPARQL endpoint URL constructed from the root URL
 * @constant {string} SPARQL_ENDPOINT
 */
const SPARQL_ENDPOINT = `${ROOT_URL}sparql`
// const SPARQL_ENDPOINT = `http://localhost/sparql`

/**
 * Executes a SPARQL query against the Whyis SPARQL endpoint
 * @param {string} query - The SPARQL query string to execute
 * @returns {Promise<Object>} Promise that resolves to the SPARQL results in JSON format
 * @throws {Error} If the SPARQL query fails or returns an error
 * @example
 * const results = await querySparql(`
 *   SELECT ?subject ?predicate ?object
 *   WHERE { ?subject ?predicate ?object }
 *   LIMIT 10
 * `);
 * console.log(results.results.bindings);
 */
function querySparql(query) {
  const request = {
    method: 'post',
    url: SPARQL_ENDPOINT,
    data: `query=${encodeURIComponent(query)}`,
    headers: {
      'Accept': 'application/sparql-results+json',
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    },
    withCredentials: true
  }
  return axios(request)
    .then(response => response.data)
}

export { querySparql }
