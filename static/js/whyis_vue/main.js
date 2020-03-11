import Vue from 'vue'
import * as VueMaterial from 'vue-material'
import axios from 'axios'
import './components'
import nanopubMixin from './mixins/nanopub-mixin'

Vue.use(VueMaterial.default)
Vue.mixin(nanopubMixin)

let data
if (typeof (ATTRIBUTES) !== 'undefined') {
  data = {
    attributes: ATTRIBUTES,
    uri: NODE_URI,
    description: DESCRIPTION,
    user: USER,
    node: NODE,
    root_url: ROOT_URL,
    base_rate: BASE_RATE,
    lod_prefix: LOD_PREFIX,
    axios: axios
  }
} else {
  data = {}
}
new Vue({
  el: '#page',
  data
})
