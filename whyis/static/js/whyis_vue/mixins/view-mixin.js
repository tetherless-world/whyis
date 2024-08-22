import { DEFAULT_VIEWS, getCurrentUri, getCurrentView } from '../utilities/views'
/**
 * mixin providing common functions useful for whyis views.
 */
const viewMixin = {
  data: () => ({DEFAULT_VIEWS}),
  computed: {
    pageUri: getCurrentUri,
    pageView: getCurrentView,
  }
}

export default viewMixin
