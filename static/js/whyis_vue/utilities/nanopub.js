import axios from 'axios'

const nanopubBaseUrl = `${ROOT_URL}pub`
const lodPrefix = LOD_PREFIX

function getNanopubUrl (id) {
  return `${nanopubBaseUrl}/${id}`
}

function getNanopubDescribeUrl (uri) {
  return `${ROOT_URL}about?uri=${uri}&view=describe`
}

function describeNanopub (uri) {
  console.log(`loading nanopub ${uri}`)
  return axios.get(getNanopubDescribeUrl(uri))
    .then((response) => {
      console.log('received nanopub data for uri:', uri, response)
      return response.data
    })
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

function postNewNanopub (pub) {
  const request = {
    method: 'post',
    url: nanopubBaseUrl,
    data: pub,
    headers: {
      'Content-Type': 'application/ld+json'
    }
  }
  return axios(request)
    .then((response) => {
      console.log('we done it', response)
      return response
    })
}

function updateNanopub (pub) {

}

export { getLocalNanopub, describeNanopub, postNewNanopub, updateNanopub, lodPrefix }
