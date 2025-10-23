
/**
 * Utilities for managing views and navigation within the Whyis application.
 * Provides constants and functions for handling different view types and URIs.
 * 
 * @module views
 */

/**
 * Default view modes available in the application
 * @constant {Object} DEFAULT_VIEWS
 * @property {string} NEW - Create new content view
 * @property {string} EDIT - Edit existing content view  
 * @property {string} VIEW - Read-only content view
 */
const DEFAULT_VIEWS = Object.freeze({
  NEW: 'new',
  EDIT: 'edit',
  VIEW: 'view'
})

/**
 * URI mappings for specific view types
 * @constant {Object} VIEW_URIS
 * @property {string} CHART_EDITOR - URI for chart editor view
 * @property {string} SPARQL_TEMPLATES - URI for SPARQL template view
 */
const VIEW_URIS = Object.freeze({
  CHART_EDITOR: "http://semanticscience.org/resource/Chart",
  SPARQL_TEMPLATES: "http://vocab.rpi.edu/whyis/SparqlTemplate"
})

/**
 * Gets the current node URI from the global NODE_URI variable
 * @returns {string} The current node URI
 */
function getCurrentUri () {
  return window.NODE_URI
}

/**
 * Extracts the current view parameter from the URL query string
 * @returns {string|null} The view parameter value or null if not present
 * @example
 * // URL: /about?view=edit&uri=example
 * getCurrentView() // returns 'edit'
 */
function getCurrentView () {
  const params = new URLSearchParams(window.location.search)
  const view = params.get('view')
  return view
}

/**
 * Constructs a URL for viewing a specific URI with an optional view parameter
 * @param {string} uri - The URI to view
 * @param {string} [view] - Optional view mode (defaults to 'view' if provided)
 * @returns {string} The constructed URL
 * @example
 * getViewUrl('http://example.com/resource', 'edit')
 * // returns '/about?view=edit&uri=http%3A//example.com/resource'
 */
function getViewUrl(uri, view) {
    uri  = encodeURIComponent(uri);
    if (view != null) {
        return `${window.ROOT_URL}about?view=${view || 'view'}&uri=${uri}`
    }
    else {
        return `${window.ROOT_URL}about?uri=${uri}`
    }
}

/**
 * Navigates to a specific view for a given URI
 * @param {string} uri - The URI to navigate to
 * @param {string} view - The view mode to use
 * @param {string} [args] - Optional window method name ('open' to open in new tab)
 * @returns {Window|string} New window object if args='open', otherwise sets window.location
 * @example
 * goToView('http://example.com/resource', 'edit') // Navigate in current window
 * goToView('http://example.com/resource', 'view', 'open') // Open in new tab
 */
function goToView(uri, view, args) {
  if(args){
    return window[args](getViewUrl(uri, view), '_blank')
  }
  return window.location = getViewUrl(uri, view)
}

export { DEFAULT_VIEWS, VIEW_URIS, getCurrentUri, getCurrentView, getViewUrl, goToView }
