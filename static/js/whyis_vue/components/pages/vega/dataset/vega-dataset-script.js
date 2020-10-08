import Vue from 'vue';
import { EventServices } from '../../../../modules';
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import { getDefaultDataset, loadDataset, saveDataset } from "utilities/dataset-upload";
import { goToView } from "utilities/views";
import axios from 'axios';
import { lodPrefix } from 'utilities/nanopub'; 

Vue.use(VueMaterial);

const STATUS_INITIAL = 0, STATUS_SAVING = 1, STATUS_SUCCESS = 2, STATUS_FAILED = 3;
const { v4: uuidv4 } = require('uuid');
const datasetId = uuidv4();



export default Vue.component('vega-dataset', {
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
            distribution:{
              accessURL: null,
            },
            depiction: {
              name: '',
              accessURL: null,
            }
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
          uploadFieldName: 'distributions',
        filter: false,
        bottomPosition:'md-bottom-right',
        speedDials: EventServices.speedDials,
        authenticated: EventServices.authUser,
        loading: false,
        loadingText: "Loading Existing Datasets"
    }
},
methods: {


    loadDataset () {
        // console.log("loading")
        let getDatasetPromise
        if (this.pageView === 'new') {
          getDatasetPromise = Promise.resolve(getDefaultDataset())
        } else {
          getDatasetPromise = loadDataset(this.pageUri)
        }
        getDatasetPromise
          .then(dataset => {
            this.dataset = dataset;
            this.loading = false;
          })
      },
  
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
  
      distrChange(fieldName, fileList) {
        // handle file changes
        let distrData = new FormData(); 
  
        if (!fileList.length) {return this.distrStatus = STATUS_INITIAL}; 
  
        // append the files to FormData
        Array
          .from(Array(fileList.length).keys())
          .map(x => {
            distrData.append(fileList[x].name, fileList[x]); 
          });
  
        // save it
        this.saveDistribution(distrData);
      }, 
  
      saveDistribution(distrData) {
        // const uri = `${lodPrefix}/dataset/${this.generatedUUID}/distributions`
        const uri = `http://192.168.33.10:5000/dataset/${this.generatedUUID}/distributions`
        this.distrStatus = STATUS_SAVING; 
        var data = {
            'file': distrData,
            'upload_type': 'http://www.w3.org/ns/dcat#Dataset', 
            'content_type': 'multipart/form-data'
        }
        return axios.post(uri, data=data)
        .then(x => {
          this.dataset.distribution.accessURL = uri;
          this.distrStatus = STATUS_SUCCESS; 
        })
        .catch(err => { 
          this.uploadError = err.response;
          this.distrStatus = STATUS_FAILED;
        });
      }, 
  
      saveRepImg(fieldName, fileList) {
        // const uri = `${lodPrefix}/dataset/${this.generatedUUID}/depiction
        const uri = `http://192.168.33.10:5000/dataset/${this.generatedUUID}/depiction`;
        this.depictStatus = STATUS_SAVING; 
        if (!fileList.length){return this.depictStatus = STATUS_INITIAL} 
  
        let formdata = new FormData();
        formdata.append('depiction', fileList[0]) 
  
        var data = {
          'file': formdata,
          'upload_type': 'http://purl.org/net/provenance/ns#File',
          'content_type': 'multipart/form-data'
        }
  
        const request = {
          method: 'post',
          url: uri, 
          data: data,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
  
        return axios(request)
        .then(x => {  
          this.dataset.depiction.accessURL = uri;
          this.dataset.depiction.name=fileList[0].name;
          this.depictStatus = STATUS_SUCCESS;
        })
        .catch(err => { 
          this.uploadError = err.response;
          this.depictStatus = STATUS_FAILED;
        }); 
        
      }, 
  
      previewFile() { 
        const preview = document.querySelector('#depictImg');
        const wrapper = document.querySelector('#depictWrapper')
        const file = document.querySelector('#repImgUploader').files[0]; 
        const reader = new FileReader();
      
        reader.addEventListener("load", function () { 
          wrapper.style.visibility = "visible";
          preview.src = reader.result;
        }, false);
      
        if (file) {  
          reader.readAsDataURL(file);
        }
      },
  
      setDone (id, index) {
        this[id] = true;
        // console.log(this.generatedUUID)
  
        if (index) {
          this.active = index;
        };
      },
  
      submitForm: function () {
        try { 
          saveDataset(this.dataset, this.generatedUUID) 
          // console.log(this.dataset)
          .then(() => goToView(this.dataset.uri, "view"));
        } catch(err) { 
          this.uploadError = err.response;
          this.distrStatus = STATUS_FAILED;
        }
      },   
  




    showFilterBox () {
    EventServices.$emit('open-filter-box', {open: true, type: "filter"});
    return this.filter = true
    },
    newChart(){
    return EventServices.navTo("new", true)
    },
    cancelFilter(){
    return EventServices.cancelChartFilter();
    }
},
// mounted(){
//     this.loading = false,
//     setTimeout(() => {
//         this.loading = false
//     }, 2000)
// },
created() { 
    if(EventServices.authUser == undefined){
        return EventServices.navTo('view', true)
    } 
    this.loading = true;
    this.loadDataset();
    EventServices
    .$on('close-filter-box', (data) => this.filter = data)
    .$on('isauthenticated', (data) => this.authenticated = data)
}
})