//__webpack_public_path__ = ROOT_URL+'static/dist/';
import { createApp } from 'vue'
import axios from 'axios'
import './modules'
import { componentsList } from './components'

import {store} from './store'
import Header from './components/utils/header.vue'
import Drawer from './components/utils/drawer.vue'
import "./assets/css/main.scss";

// MDBootstrap
import 'mdb-vue-ui-kit/css/mdb.min.css'

// import dialogBox from './components/utils/dialog'
import viewMixin from './mixins/view-mixin'

function createWhyisApp() {
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

    const app = createApp({
	data() {
	    return data
	},
	components: {
	    //    mdAppToolbar: Header,
	    //    mdAppDrawer: Drawer,
	    // dialogBox
	}
    })
    
    app.use(store)
    app.mixin(viewMixin)
    
    // Register components
    componentsList.forEach(({ name, component }) => {
        app.component(name, component)
    })
    
    return app;
}

export {axios, createWhyisApp}
