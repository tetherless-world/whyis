import axios from 'axios'

const SPARQL_ENDPOINT = `${ROOT_URL}sparql`
// const SPARQL_ENDPOINT = `http://localhost/sparql`

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
