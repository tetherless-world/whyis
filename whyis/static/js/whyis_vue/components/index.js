//import './utils/spinner.vue'
//import './utils/dialog.vue'
import './pages'
//import "./kgcard.vue";
//import "./search-autocomplete.vue";
import "./table-view";
//import './yasqe.vue';
//import './yasr.vue';
import './gallery';
//import './add-type.vue';
//import './add-attribute.vue';
//import './add-link.vue';
//import './upload-knowledge.vue';
//import './upload-file.vue';
//import './add-knowledge-menu.vue';
//import './accordion.vue'
//import './album.vue'

import Vue from 'vue';

Vue.component('vega-lite', () => import('./vega-lite-wrapper.vue'))
Vue.component('spinner', () => import('./utils/spinner.vue'))
Vue.component('dialogBox', () => import('./utils/dialog.vue'))
Vue.component('kgcard', () => import('./kgcard.vue'))
Vue.component('search-autocomplete', () => import('./search-autocomplete.vue'))
Vue.component('album', () => import('./album.vue'))
Vue.component('add-type', () => import('./add-type.vue'))
Vue.component('add-attribute', () => import('./add-attribute.vue'))
Vue.component('add-link', () => import('./add-link.vue'))
Vue.component('upload-knowledge', () => import('./upload-knowledge.vue'))
Vue.component('upload-file', () => import('./upload-file.vue'))
Vue.component('add-knowledge-menu', () => import('./add-knowledge-menu.vue'))

Vue.component('accordion', () => import('./accordion.vue'))

Vue.component('yasqe', () => import('./yasqe.vue'))
Vue.component('yasr', () => import('./yasr.vue'))

