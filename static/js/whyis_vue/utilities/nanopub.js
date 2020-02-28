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
  console.log(`loading nanopub ${uri}`)
  return axios.get(`${ROOT_URL}about?view=describe&uri=${encodeURIComponent(uri)}`)
    .then((response) => {
      console.log('received nanopub data for uri:', uri, response)
      return response.data
    })
}

function listNanopubs (uri) {
  return axios.get(`${ROOT_URL}about?view=nanopublications&uri=${encodeURIComponent(uri)}`)
}

function getLocalNanopub (id) {
  console.log(`loading nanopub ${id}`)
  const url = getNanopubUrl(id)
  return axios.get(url)
    .then((response) => {
      console.log('received nanopub data for url:', url, response)
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
      console.log('we done it', response)
      describeNanopub(response.headers.location)
      describeNanopub(pubData['@id'])
      listNanopubs(pubData['@id'])
      return response
    })
}

function deleteNanopub (uri) {
  return axios.delete(getAboutUrl(uri))
}

export {
  listNanopubs,
  getLocalNanopub,
  describeNanopub,
  postNewNanopub,
  lodPrefix
}
