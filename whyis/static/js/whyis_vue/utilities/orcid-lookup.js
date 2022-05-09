
import axios from 'axios';

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