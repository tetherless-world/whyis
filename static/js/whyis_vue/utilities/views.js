
const DEFAULT_VIEWS = Object.freeze({
  NEW: 'new',
  EDIT: 'edit',
  VIEW: 'view'
})

function getCurrentUri () {
  const params = new URLSearchParams(window.location.search)
  const uri = params.get('uri')
  return uri
}

function getCurrentView () {
  const params = new URLSearchParams(window.location.search)
  const view = params.get('view')
  return view
}

function getViewUrl(uri, view) {
  return `${ROOT_URL}about?view=${view}&uri=${uri}`
}

function goToView(uri, view) {
  window.location = getViewUrl(uri, view)
}

export { DEFAULT_VIEWS, getCurrentUri, getCurrentView, getViewUrl, goToView }
