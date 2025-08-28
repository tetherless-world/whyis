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

// core/componentRegistry.js
class ComponentRegistry {
  constructor() {
    this.components = new Map();
    this.extensions = new Map();
  }

  registerComponent(name, component, metadata = {}) {
    this.components.set(name, {
      component,
      metadata,
      timestamp: Date.now()
    });
    
    // Auto-register with Vue if instance exists
    if (window.vueApp) {
      window.vueApp.component(name, component);
    }
  }

  getComponent(name) {
    return this.components.get(name);
  }

  getAllComponents() {
    return Array.from(this.components.entries());
  }
}

// Make globally available
window.ComponentRegistry = new ComponentRegistry();

class ExtensionLoader {
  static createExtension(config) {
    const extension = {
      name: config.name,
      version: config.version,
      components: config.components || {},
      init: config.init || (() => {}),
      destroy: config.destroy || (() => {})
    };

    // Register all components from this extension
    Object.entries(extension.components).forEach(([name, component]) => {
      window.ComponentRegistry.registerComponent(name, component, {
        extension: extension.name,
        version: extension.version
      });
    });

    // Store extension reference
    window.ComponentRegistry.extensions.set(extension.name, extension);
    
    // Initialize extension
    extension.init();
    
    return extension;
  }
}

window.ExtensionLoader = ExtensionLoader;

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

// Register any pre-existing components
window.ComponentRegistry.getAllComponents().forEach(([name, { component }]) => {
  app.component(name, component);
});

export {app, axios}
