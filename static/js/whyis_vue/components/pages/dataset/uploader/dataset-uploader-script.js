import Vue from "vue"; 
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import { getDefaultDataset, saveDataset } from "utilities/dataset-upload"; //Change this
import { goToView } from "utilities/views";

Vue.use(VueMaterial);

export default Vue.component('dataset-uploader', {  
  data() {
    return {
      dataset: {
        title: "",
        description: "",
        contactpoint: {
          "@type": "individual",
          cpfirstname: "",
          cplastname: "",
          cpemail: "",
        },
        contributor: [],
        author: [],
        datepub: {
          "@type": "date",
          "@value": "",
        },
        datemod: {
          "@type": "date",
          "@value": "",
        },
        refby: [],
      },

      dois: "",
      contributors: [],
      distribution: [],
      rep_image: [],
      active: "first",
      first: false,
      second: false,
      third: false,
    };
  },
  methods: {
    addOrg: function () {
      var elem = document.createElement("tr");
      this.contributors.push({
        org: "",
        authors: "",
      });
    },
    dateFormat(value, event) {
      return moment(value).format("YYYY-MM-DD");
    },
    removeElement: function (index) {
      this.contributors.splice(index, 1);
    },
    editDois: function () {
      var doisseparated = this.dois.split(/[ ,]+/);
      this.dataset.refby = doisseparated.map((x) => "https://dx.doi.org/" + x);
    },
    setContributors: function (index) {
      var contr = this.contributors[index]["org"]; //TODO
      this.dataset.contributor[index] = {
        "@type": "organization",
        name: contr,
      };
    },
    setAuthors: function (org, name) {
      if (org === ""){
        this.dataset.author.push({
          "@type": "person",
          name: name,
        })
      } else {
      this.dataset.author.push({
        "@type": "person",
        name: name,
        onbehalfof: {
          "@type": "organization",
          name: org,
        },
      })
      };
    },
    submitForm: function () {
      for (var index in this.contributors) {
        this.setContributors(index);
        var org = this.contributors[index]["org"];
        const auths = this.contributors[index]["authors"].split(",");
        auths.forEach((x) => this.setAuthors(org, x));
      }
      console.log(JSON.stringify(this.dataset));
      saveDataset(this.dataset);
    }, 
    loadDataset() {
      let getDatasetPromise;
      getDatasetPromise = Promise.resolve(getDefaultDataset());
      getDatasetPromise.then((chart) => {
        this.chart = chart;
        this.getSparqlData();
      });
    },
    // saveDataset() {
    //   console.log(this._data);
    //   saveDataset(this._data).then(() => goToView(this._dataset.uri, "edit"));
    // },
    setDone (id, index) {
      this[id] = true;

      if (index) {
        this.active = index;
      };
    },
  },
});
