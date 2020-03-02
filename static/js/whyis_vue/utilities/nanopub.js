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

function postNewNanopub (pubData) {
  const request = {
    method: 'post',
    url: nanopubBaseUrl,
    data: pubData,
    headers: {
      'Content-Type': 'application/ld+json'
    }
  }
  return axios(request)
    .then((response) => {
      console.debug('we done it', response)
      describeNanopub(response.headers.location)
      describeNanopub(pubData['@id'])
      listNanopubs(pubData['@id'])
      return response
    })
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
