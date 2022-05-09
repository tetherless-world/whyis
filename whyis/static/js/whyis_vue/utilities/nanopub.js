import axios from 'axios'

const nanopubBaseUrl = `${ROOT_URL}pub`
const lodPrefix = LOD_PREFIX

function getNanopubUrl (id) {
  return `${nanopubBaseUrl}/${id}`
}

function getAboutUrl(uri) {
  return `${ROOT_URL}about?uri=${uri}`
}

function describeNanopub (uri) {
  console.debug(`loading nanopub ${uri}`)
  return axios.get(`${ROOT_URL}about?view=describe&uri=${encodeURIComponent(uri)}`)
    .then((response) => {
      console.debug('received nanopub data for uri:', uri, response)
      return response.data
    })
}

function listNanopubs (uri) {
  return axios.get(`${ROOT_URL}about?view=nanopublications&uri=${encodeURIComponent(uri)}`)
    .then(response => {
      console.debug('list nanopub response', response)
      return response.data
    })
}

function getLocalNanopub (id) {
  console.debug(`loading nanopub ${id}`)
  const url = getNanopubUrl(id)
  return axios.get(url)
    .then((response) => {
      console.debug('received nanopub data for url:', url, response)
      return response
    })
}

function makeNanopubId() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return Math.random().toString(36).substr(2, 10);
}

function getNanopubSkeleton () {
  //doot
  const npId = `${lodPrefix}/pub/${makeNanopubId()}` //make sure this change doesn't break other things
  return {
    "@context": {
      "@vocab": lodPrefix+'/',
      "@base": lodPrefix+'/',
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

function postNewNanopub (pubData, context) {
  const nanopub = getNanopubSkeleton()
  if (context) {
    nanopub['@context'] = {...nanopub['@context'], ...context}
  }
  nanopub['@graph']['np:hasAssertion']['@graph'].push(pubData)
  const request = {
    method: 'post',
    url: nanopubBaseUrl,
    data: nanopub,
    headers: {
      'Content-Type': 'application/ld+json'
    }
  }
  // console.log(request)
  return axios(request)
}

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
