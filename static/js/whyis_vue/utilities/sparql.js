import axios from 'axios'

const SPARQL_ENDPOINT = `${ROOT_URL}sparql`

function querySparql(query) {
  const request = {
    method: 'post',
    url: SPARQL_ENDPOINT,
    data: `query=${encodeURIComponent(query)}`,
    headers: {
      'Accept': 'application/sparql-results+json',
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
  }
  return axios(request)
    .then(response => response.data)
}

export { querySparql }
