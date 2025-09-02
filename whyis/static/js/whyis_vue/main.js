/**
 * Main entry point for the Whyis Vue.js application.
 * Configures Vue, registers components, and provides the application bootstrap function.
 * 
 * @module main
 */

//__webpack_public_path__ = ROOT_URL+'static/dist/';
import Vue from 'vue'
import * as VueMaterial from 'vue-material'
import axios from 'axios'
import './modules'
import './components'

import {store} from './store'
import Header from './components/utils/header.vue'
import Drawer from './components/utils/drawer.vue'
import "./assets/css/main.scss";

// import dialogBox from './components/utils/dialog'
import viewMixin from './mixins/view-mixin'

// Configure Vue with Material Design components
Vue.use(VueMaterial.default)
Vue.mixin(viewMixin)

// As per https://github.com/vuematerial/vue-material/issues/2285#issuecomment-1059410143
// Vue.component('MdSelect', Vue.options.components.MdFile.extend({
//     methods: {
//         isInvalidValue: function isInvalidValue () {
//             return this.$el.validity ? this.$el.validity.badInput : this.$el.querySelector('input').validity.badInput
//         }
//     }
// }))

import { MdField } from 'vue-material/dist/components'

Vue.use(MdField)

/**
 * Extended MdSelect component with improved form validation
 * Fixes badInput validation for select fields in Material Design components
 */
Vue.component('MdSelect', Vue.options.components.MdSelect.extend({
    methods: {
        /**
         * Validates the input field and returns validation state
         * @returns {boolean} True if the input has validation errors
         */
        isInvalidValue: function isInvalidValue () {
            return this.$el.validity ? this.$el.validity.badInput : this.$el.querySelector('input').validity.badInput
        }
    }
}))

/**
 * Creates and initializes the main Vue application instance
 * @returns {Vue} The configured Vue application instance
 * 
 * @example
 * // Initialize the Whyis application
 * const app = createApp();
 * // The app is automatically mounted to the #page element
 */
function createApp() {
    let data = {}
    if (typeof (ATTRIBUTES) !== 'undefined') {
	data = {
	    attributes: ATTRIBUTES,     // Node attributes from server
	    summary: SUMMARY,           // Node summary data
	    nav: NAVIGATION,            // Navigation configuration
	    uri: NODE_URI,              // Current node URI
	    description: DESCRIPTION,   // Node description
	    user: USER,                 // Current user information
	    node: NODE,                 // Current node data
	    root_url: ROOT_URL,         // Application root URL
	    base_rate: BASE_RATE,       // Base rate configuration
	    lod_prefix: LOD_PREFIX,     // Linked Open Data prefix
	    showUploadDialog: false,    // Upload dialog visibility state
	    window_state: {},           // Window state management
	    axios: axios,               // HTTP client instance
	}
    }

    var app = new Vue({
	el: '#page',
	data,
	store,
	
	components: {
	    //    mdAppToolbar: Header,
	    //    mdAppDrawer: Drawer,
	    // dialogBox
	}
    })
    return app;
}

/**
 * Exported modules for external use
 * @namespace
 * @property {Vue} Vue - Vue constructor for creating components
 * @property {axios} axios - HTTP client for API requests
 * @property {Function} createApp - Application bootstrap function
 */
export {Vue, axios, createApp}
