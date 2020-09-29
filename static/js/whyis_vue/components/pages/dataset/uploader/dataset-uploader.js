import Vue from "vue"; 
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import { getDefaultDataset, saveDataset } from "utilities/dataset-upload"; //Change this
import { goToView } from "utilities/views";

Vue.use(VueMaterial);

export default Vue.component('dataset-uploader', {
  // el: "#datasetupload", 
  name: "TextFields",
  data: () => ({
    title: "",
    cpfirstname: "",
    cplastname: "",
    cpemail: "",
    textdescription: "",
    contributors: [],
    datepub: null,
    datemod: "",
    dois: [],
  }),
  methods: {
    addOrg: function () {
      var elem = document.createElement("tr");
      this.contributors.push({
        org: "",
        authors: "",
      });
    },
    removeElement: function (index) {
      this.contributors.splice(index, 1);
    },
    submitForm: function () {
      console.log(JSON.stringify(this._data));
    }, 
    loadDataset() {
      let getDatasetPromise;
      getDatasetPromise = Promise.resolve(getDefaultDataset());
      getDatasetPromise.then((chart) => {
        this.chart = chart;
        this.getSparqlData();
      });
    },
    saveDataset() {
      console.log(this._data);
      saveDataset(this._data).then(() => goToView(this._dataset.uri, "edit"));
    }
  }
});
