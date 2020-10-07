import Vue from "vue"; 
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import { getDefaultDataset, saveDataset } from "utilities/dataset-upload"; //Change this
import { goToView } from "utilities/views";
import * as axios from 'axios'
import { lodPrefix } from 'utilities/nanopub'

Vue.use(VueMaterial);

const STATUS_INITIAL = 0, STATUS_SAVING = 1, STATUS_SUCCESS = 2, STATUS_FAILED = 3;
const { v4: uuidv4 } = require('uuid');
const datasetId = uuidv4();

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

        distribution: [],
        depiction: []
      },

      generatedUUID: datasetId,

      dois: "",
      contributors: [],
      distr_upload: [],
      rep_image: [],

      // Stepper data
      active: "first",
      first: false,
      second: false,
      third: false,

      //handle uploads
      uploadedFiles: [],
      uploadError: null,
      currentStatus: null,
      distrStatus: null,
      depictStatus: null,
      isInvalid: false,
    };
  },
  computed: {
    isInitialDepict() {
      return this.depictStatus === STATUS_INITIAL;
    },
    isSavingDepict() {
      return this.depictStatus === STATUS_SAVING;
    },
    isSuccessDepict() {
      return this.depictStatus === STATUS_SUCCESS;
    },
    isFailedDepict() {
      return this.depictStatus === STATUS_FAILED;
    },


    isInitialDistr(){
      return this.distrStatus === STATUS_INITIAL;
    },
    isSavingDistr() {
      return this.distrStatus === STATUS_SAVING;
    },
    isSuccessDistr() {
      return this.distrStatus === STATUS_SUCCESS;
    },
    isFailedDistr() {
      return this.distrStatus === STATUS_FAILED;
    },
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
    handleContrAuth: function () {
      //Ensure the fields are cleared to avoid duplication
      this.dataset.contributor = [];
      this.dataset.author = [];
      for (var index in this.contributors) {
        this.setContributors(index);
        var org = this.contributors[index]["org"];
        const auths = this.contributors[index]["authors"].split(",");
        auths.forEach((x) => this.setAuthors(org, x));
      }
    },
    setContributors: function (index) {
      var contr = this.contributors[index]["org"];
      if (contr !== ""){
        this.dataset.contributor.push({
          "@type": "organization",
        name: contr,
        })
      };
    },
    setAuthors: function (org, name) {
      if (name !==""){
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
      } 
    },
    submitForm: function () {
      try { 
        saveDataset(this.dataset, this.generatedUUID)
      } catch(err) { 
        this.uploadError = err.response;
        this.distrStatus = STATUS_FAILED;
      }
      // .then(() => goToView(this.dataset.uri, "edit"));
    },   

    distrChange(fieldName, fileList) {
      // handle file changes
      const distrData = new FormData(); 

      if (!fileList.length) {return this.distrStatus = STATUS_INITIAL};

      // append the files to FormData
      Array
        .from(Array(fileList.length).keys())
        .map(x => {
          distrData.append(fieldName, fileList[x], fileList[x].name);
        });

      // save it
      this.saveDistribution(distrData);
    }, 

    saveDistribution(distrData) {
      const uri = `${lodPrefix}/dataset/${this.generatedUUID}/distributions`
      this.distrStatus = STATUS_SAVING; 
      var data = {
          'file': distrData,
          'upload_type': 'http://www.w3.org/ns/dcat#Dataset', 
          'content_type': 'multipart/form-data'
      }
      return axios.post(uri, data=data)
      .then(x => {
        this.dataset.distribution = [].concat(x);
        this.distrStatus = STATUS_SUCCESS;
      })
      .catch(err => {
        console.log(data)
        this.uploadError = err.response;
        this.distrStatus = STATUS_FAILED;
      });
    }, 

    saveRepImg(fieldName, fileList) {
      const uri = `${lodPrefix}/dataset/${this.generatedUUID}/depiction`
      this.depictStatus = STATUS_SAVING; 
      if (!fileList.length){return this.depictStatus = STATUS_INITIAL}

      var data = {
          'file': fileList[0],
          'upload_type': 'http://purl.org/net/provenance/ns#File',
          'content_type': 'multipart/form-data'
      }
      return axios.post(uri, data=data)
      .then(x => { 
        this.dataset.depiction = uri;
        this.depictStatus = STATUS_SUCCESS;
      })
      .catch(err => { 
        console.log(data)
        this.uploadError = err.response;
        this.depictStatus = STATUS_FAILED;
      });
    }, 

    setDone (id, index) {
      this[id] = true;
      console.log(this.generatedUUID)

      if (index) {
        this.active = index;
      };
    },
  },
});
