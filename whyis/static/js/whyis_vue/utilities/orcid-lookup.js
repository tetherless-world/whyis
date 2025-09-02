
/**
 * ORCID (Open Researcher and Contributor ID) lookup utilities.
 * Provides functions to validate ORCID IDs and retrieve associated researcher data.
 * 
 * @module orcid-lookup
 */

import axios from 'axios';

/**
 * Looks up ORCID data for a given ORCID ID through the Whyis API
 * @param {string} inputOrcidId - The ORCID ID to lookup (with or without hyphens)
 * @param {string} type - The type of lookup being performed (e.g., "contactPoint")
 * @returns {Promise<Object|string>} The ORCID data object or "Invalid" for invalid IDs
 * @example
 * const orcidData = await lookupOrcid('0000-0000-0000-0000', 'contactPoint');
 */
export default async function lookupOrcid(inputOrcidId, type) {
  // Get the data for this ORCID id through Whyis using view=describe
  if (isValidOrcidId(inputOrcidId)){
    var response = await axios.get(`/orcid/${inputOrcidId}?view=describe`, {
      headers: {
        'Accept': 'application/ld+json',
      }
    })
    var orcidId = response.data;
    orcidId = findCorrectEntry(orcidId, `http://orcid.org/${inputOrcidId}`, type)
    return orcidId
  }
  else {
    // Invalid ORCID id
    return "Invalid";
  }
}

/**
 * Validates ORCID ID format, accepting both hyphenated and unhyphenated formats
 * @param {string} inputOrcidId - The ORCID ID to validate
 * @returns {boolean} True if the ORCID ID format is valid, false otherwise
 * @example
 * isValidOrcidId('0000-0000-0000-0000') // returns true
 * isValidOrcidId('0000000000000000') // returns true
 * isValidOrcidId('invalid-id') // returns false
 */
function isValidOrcidId(inputOrcidId){
  // Check for valid ORCID id format
  const regUnhyphenated = /^\d{16}$/
  const unhyphenated = regUnhyphenated.test(inputOrcidId);
  if (unhyphenated){
    inputOrcidId = inputOrcidId.replace(/^\(?([0-9]{4})\)?([0-9]{4})?([0-9]{4})?([0-9]{4})$/, "$1-$2-$3-$4")
  }
  const regHyphenated = /^\(?([0-9]{4})\)?[-]?([0-9]{4})[-]?([0-9]{4})[-]?([0-9]{4})$/;
  return regHyphenated.test(inputOrcidId);
}

/**
 * Extracts the correct entry from ORCID response data based on the target ID
 * @param {Object} responseData - The full response data from ORCID lookup
 * @param {string} correctId - The specific ORCID URI to find in the response
 * @param {string} type - The type of lookup for handling empty responses
 * @returns {Object|undefined} The matching entry or undefined if not found
 */
function findCorrectEntry(responseData, correctId, type){
  if ('@graph' in responseData){
      // If invalid id, graph will be empty so return nothing
      if (!responseData['@graph'].length){
        if (type == "contactPoint"){
          return this.resetContactPoint(); 
        }
      return
      }
      // Look for the entry that corresponds to the actual id
      for (var entry in responseData['@graph']){
      if (responseData['@graph'][entry]['@id'] === correctId){
          return responseData['@graph'][entry]
      }
      }
  }
  else{
    return responseData
  }
}

export {lookupOrcid}