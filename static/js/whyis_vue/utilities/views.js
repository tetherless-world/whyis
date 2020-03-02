
function getViewUrl(uri, view) {
  return `${ROOT_URL}about?view=${view}&uri=${uri}`
}

function goToView(uri, view) {
  window.location = getViewUrl(uri, view)
}

export { getViewUrl, goToView }
