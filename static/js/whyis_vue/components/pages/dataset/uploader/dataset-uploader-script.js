import Vue from 'vue' 

import { goToView } from 'utilities/views'

export default Vue.component('dataset-uploader', {
  components: { 
  },
  data () {
    return {
      chart: {
        baseSpec: null,
        query: null,
        title: null,
        description: null
      },
      results: null,
      chartPub: null,
      specJsonEditorOpts: {
        mode: 'code',
        mainMenuBar: false
      }
    }
  },
})

// import Vue from "vue";
// import App from "./App";
// import VueMaterial from "vue-material";
// import "vue-material/dist/vue-material.min.css";
// import "vue-material/dist/theme/default.css";
// import { getDefaultDataset, saveDataset } from "./dataset-upload"; //Change this
// import { goToView } from "./utilities/views";

// Vue.use(VueMaterial);

// new Vue({
//   el: "#app",
//   components: { App },
//   template: "<App/>",
//   methods: {
//     loadDataset() {
//       let getDatasetPromise;
//       getDatasetPromise = Promise.resolve(getDefaultDataset());
//       getDatasetPromise.then((chart) => {
//         this.chart = chart;
//         this.getSparqlData();
//       });
//     },
//     saveDataset() {
//       console.log(this._data);
//       saveDataset(this._data).then(() => goToView(this._dataset.uri, "edit"));
//     }
//   }
// });
