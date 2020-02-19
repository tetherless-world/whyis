/**
 * Vue mixin providing common functions useful for whyis nanopub pages.
 */
const nanopubMixin = {
  computed: {
    /**
     * Get the nanopub uri for the current page.
     */
    pageUri () {
      const params = new URLSearchParams(window.location.search)
      const uri = params.get('uri')
      console.log('computed uri', uri)
      return uri
    },
    /**
     * Get the view for the current page.
     */
    pageView () {
      const params = new URLSearchParams(window.location.search)
      const view = params.get('view')
      console.log('computed view', view)
      return view
    }
  }
}

export default nanopubMixin
