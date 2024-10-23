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

Vue.component('MdSelect', Vue.options.components.MdSelect.extend({
    methods: {
        isInvalidValue: function isInvalidValue () {
            return this.$el.validity ? this.$el.validity.badInput : this.$el.querySelector('input').validity.badInput
        }
    }
}))

function createApp() {
    let data = {}
    if (typeof (ATTRIBUTES) !== 'undefined') {
	data = {
	    attributes: ATTRIBUTES,
	    summary: SUMMARY,
	    nav: NAVIGATION,
	    uri: NODE_URI,
	    description: DESCRIPTION,
	    user: USER,
	    node: NODE,
	    root_url: ROOT_URL,
	    base_rate: BASE_RATE,
	    lod_prefix: LOD_PREFIX,
	    showUploadDialog: false,
	    window_state: {},
	    axios: axios,
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

export {Vue, axios, createApp}
