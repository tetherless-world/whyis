/**
 * Vue mixin providing common view-related functionality for Whyis components.
 * Provides access to view constants and current page information across components.
 * 
 * @module view-mixin
 */

import { DEFAULT_VIEWS, getCurrentUri, getCurrentView } from '../utilities/views'

/**
 * Mixin providing common functions useful for whyis views.
 * Injects view constants and computed properties for URI and view detection.
 * 
 * @type {Object}
 * @property {Function} data - Returns view constants in component data
 * @property {Object} computed - Computed properties for current page context
 * @property {Function} computed.pageUri - Gets the current page URI
 * @property {Function} computed.pageView - Gets the current page view mode
 * 
 * @example
 * // In a Vue component:
 * export default {
 *   mixins: [viewMixin],
 *   // Now you can access this.DEFAULT_VIEWS, this.pageUri, this.pageView
 * }
 */
const viewMixin = {
  data: () => ({DEFAULT_VIEWS}),
  computed: {
    pageUri: getCurrentUri,
    pageView: getCurrentView,
  }
}

export default viewMixin
