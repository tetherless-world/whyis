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

// Export components for Vue 3 registration
export const componentsList = [
  { name: 'vega-lite', component: () => import('./vega-lite-wrapper.vue') },
  { name: 'spinner', component: () => import('./utils/spinner.vue') },
  { name: 'dialogBox', component: () => import('./utils/dialog.vue') },
  { name: 'kgcard', component: () => import('./kgcard.vue') },
  { name: 'search-autocomplete', component: () => import('./search-autocomplete.vue') },
  { name: 'album', component: () => import('./album.vue') },
  { name: 'add-type', component: () => import('./add-type.vue') },
  { name: 'add-attribute', component: () => import('./add-attribute.vue') },
  { name: 'add-link', component: () => import('./add-link.vue') },
  { name: 'upload-knowledge', component: () => import('./upload-knowledge.vue') },
  { name: 'upload-file', component: () => import('./upload-file.vue') },
  { name: 'add-knowledge-menu', component: () => import('./add-knowledge-menu.vue') },
  { name: 'accordion', component: () => import('./accordion.vue') },
  { name: 'yasqe', component: () => import('./yasqe.vue') },
  { name: 'yasr', component: () => import('./yasr.vue') },
  { name: 'vega-editor', component: () => import('./pages/vega/editor/vega-editor.vue') },
  { name: 'vega-gallery', component: () => import('./pages/vega/gallery/vega-gallery.vue') },
  { name: 'vega-sparql', component: () => import('./pages/vega/sparql/vega-sparql.vue') },
  { name: 'data-voyager', component: () => import('./pages/vega/data-voyager/data-voyager.vue') },
  { name: 'data-voyager-page', component: () => import('./pages/vega/data-voyager/data-voyager-page.vue') },
  { name: 'vega-viewer', component: () => import('./pages/vega/view/vega-viewer.vue') },
  { name: 'dataset-uploader', component: () => import('./pages/dataset/upload-new/dataset-uploader.vue') },
  { name: 'sparql-template-page', component: () => import('./pages/sparql-templates/sparql-template-page.vue') }
]

