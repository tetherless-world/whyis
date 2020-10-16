import Vue from 'vue';
import { EventServices } from '../../../../modules';
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";
import { getDefaultDataset, loadDataset, saveDataset, deleteDataset, processAutocompleteMenu} from "utilities/dataset-upload";
import { goToView } from "utilities/views"; 
// import { resolveEntity } from '../../../../../whyis'
import { lodPrefix } from 'utilities/nanopub';  
import axios from 'axios';

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
            '@id': null,
            hasContent: null,
          },
          depiction: {
            name: '',
            accessURL: null,
            '@id': null,
            hasContent: null,
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
        uploadedImg: [],
        uploadError: null,
        currentStatus: null,
        distrStatus: STATUS_INITIAL,
        depictStatus: STATUS_INITIAL,
        isInvalidUpload: false,
        isInvalidForm: false,
        uploadFieldName: 'distributions',
 

        selectedText: '',
        filter: false,
        bottomPosition:'md-bottom-right',
        speedDials: false,
        // speedDials: EventServices.speedDials,
        authenticated: EventServices.authUser,
        autocomplete: {
          availableInstitutions: [],
          availableAuthors: [],
          // availableInstitutions: EventServices.institutions,
          // availableAuthors: EventServices.authors, 
        },
        loading: false,
        loadingText: "Loading Existing Datasets",

      /// search
      query: null,
      selectedAuthor: [],
      items: [],
      testChips: [],
      // item: {
      //   label: '',
      //   types: [],
      // },
      // searchText: '',
    }
},
methods: {


    loadDataset () {
        console.log(this.speedDials)
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
  
      addOrg () {
        var elem = document.createElement("tr");
        this.contributors.push({
          org: "",
          authors: [],
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
          this.contributors[index]["authors"].forEach((x) => this.setAuthors(org, x));
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
      selectAuthor (index) { 
        if ((this.selectedAuthor[index] !== null)&& (this.selectedAuthor[index] !== "")){
          this.contributors[index]['authors'].push(this.selectedAuthor[index]);
        }
        console.log(this.contributors)
      },
      removeAuthor (ind, index){
        this.contributors[index]['authors'].splice(ind, 1)
        this.selectedAuthor[index] = "";
        console.log(this.contributors)
      },

      handleDistrUpload(files) { 
        let uploadedFiles = files;  
        /*
          Adds the uploaded file to the files array
        */
        for( var i = 0; i < uploadedFiles.length; i++ ){
          var curFile = uploadedFiles[i]; 
          if ( this.uploadedFiles.some(file => file.name === curFile.name) ){
            alert(`${curFile.name} has already been uploaded`)
          } else {
            this.isInvalidUpload = false;
            this.uploadedFiles.push( curFile );
          }
        } 
      }, 

      handleImgUpload(files) {   
        this.uploadedImg = files;  
      }, 

      removeFile( key ){
        this.uploadedFiles.splice( key, 1 );
        const uploader = document.querySelector('#distrFiles'); 
        this.distr_upload = [];  
        uploader.value = "";  
      },
  
      async saveDistribution() {
        let fileList = this.uploadedFiles;
        let distrData = new FormData(); 
  
        if (!fileList.length) {return this.distrStatus = STATUS_INITIAL}; 
  
        // append the files to FormData
        Array
          .from(Array(fileList.length).keys())
          .map(x => {
            distrData.append(fileList[x].name, fileList[x]); 
          });

        const uri = `${lodPrefix}/dataset/${this.generatedUUID}/distributions`;
        const baseUrl = `${window.location.origin}/about?uri=${uri}`
        // const uri = `http://192.168.33.10:5000/dataset/${this.generatedUUID}/distributions`
        this.distrStatus = STATUS_SAVING; 
        
        var data = {
            '@id': uri,
            'file': distrData,
            'upload_type': 'http://www.w3.org/ns/dcat#Dataset',  
            'content_type': 'multipart/form-data'
        }

        await fetch(baseUrl, {
          method: 'POST',
          body: data, 
          headers: {
             Accept: 'application/json',
             'Content-Type': 'multipart/form-data',
             'upload_type': 'http://www.w3.org/ns/dcat#Dataset',
          }
        })
        // return axios.post(uri, data=data)
        .then(x => {
          console.log(baseUrl) 
          this.dataset.distribution['@id'] = uri;
          this.dataset.distribution.accessURL = uri;
          this.distrStatus = STATUS_SUCCESS; 
        })
        .catch(err => { 
          this.uploadError = err.response;
          this.distrStatus = STATUS_FAILED;
        });
      }, 
  
      async saveRepImg() {
        const fileList = this.uploadedImg; 
        const uri = `${lodPrefix}/dataset/${this.generatedUUID}/depiction`;
        const baseUrl = `${window.location.origin}/about?uri=${uri}`
        // const uri = `http://192.168.33.10:5000/dataset/${this.generatedUUID}/depiction`;
        this.depictStatus = STATUS_SAVING; 
        if (!fileList.length){return this.depictStatus = STATUS_INITIAL} 
  
        let formdata = new FormData();
        formdata.append('depiction', fileList[0]) 
  
        var data = {
          '@id': uri,
          'file': formdata,
          'upload_type': 'http://purl.org/net/provenance/ns#File',
          'content_type': 'multipart/form-data'
        }
        
        await fetch(baseUrl, {
          method: 'POST',
          body: data, 
          headers: {
             Accept: 'application/json',
             'Content-Type': 'multipart/form-data',
             'upload_type':   'http://purl.org/net/provenance/ns#File',
          }
        })
        .then(x => {   
          this.dataset.depiction.accessURL = baseUrl;
          this.dataset.depiction['@id'] = uri;
          this.dataset.depiction.name=fileList[0].name;
          this.depictStatus = STATUS_SUCCESS;
        })
        .catch(err => { 
          this.uploadError = err.response;
          this.depictStatus = STATUS_FAILED;
        }); 
        
      }, 

      removeImage(){ 
        document.querySelector('#repImgUploader').value = "";
        document.querySelector('#depictImg').src=""; 
        this.rep_image = [];  
        this.uploadedImg = [];
        document.querySelector('#depictWrapper').style.visibility = "hidden"; 
      },
  
      previewFile() { 
        const preview = document.querySelector('#depictImg');
        const wrapper = document.querySelector('#depictWrapper')
        const file = document.querySelector('#repImgUploader').files[0]; 
        const reader = new FileReader();
        const dataset = this.dataset;
      
        reader.addEventListener("load", function () { 
          wrapper.style.visibility = "visible";
          preview.src = reader.result; 
          dataset.depiction.hasContent = reader.result;
        }, false);
      
        if (file) {  
          reader.readAsDataURL(file);
        }
      },

      // async imgToUrl() {
      //   let blob = await fetch("https://example.com/image.png").then(r => r.blob());
      //   let dataUrl = await new Promise(resolve => {
      //     let reader = new FileReader();
      //     reader.onload = () => resolve(reader.result);
      //     reader.readAsDataURL(blob);
      //   });
      //   // now do something with `dataUrl`
      // },

      checkFirstPage(){ 
        // // Check for at least one distribution
        // if (!this.uploadedFiles.length){
        //   this.isInvalidUpload = true;
        // } else { 
          this.saveRepImg(); 
          this.saveDistribution(); 
          this.setDone('first', 'second');
        // }
      },

      checkSecondPage(){
        // Check the required fields
        const titleBool = (this.dataset.title === "");
        const cpfirstnameBool = (this.dataset.contactpoint.cpfirstname === "");
        const cplastnameBool = (this.dataset.contactpoint.cplastname === "");
        const cpemailBool = (this.dataset.contactpoint.cpemail === "");
        const descriptionBool = (this.dataset.description === "");

        // Prevent form submission if required fields are empty
        if (titleBool || cpfirstnameBool || cplastnameBool || cpemailBool || descriptionBool){
          this.isInvalidForm = true;
        } if (!this.validEmail(this.dataset.contactpoint.cpemail)) { 
          this.dataset.contactpoint.cpemail = '';
          this.isInvalidForm = true;
        } else { 
          this.isInvalidForm = false;
          this.setDone('second', 'third'); 
          this.handleContrAuth();
        }
      },

      validEmail (email) {
        var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
      },
  
      setDone (id, index) {
        this[id] = true;
        // console.log(this.generatedUUID)
  
        if (index) {
          this.active = index;
        };
      },
  
      submitForm: function () {
        // console.log(this.dataset)
        try { 
          saveDataset(this.dataset, this.generatedUUID) 
          // console.log(this.dataset)
          .then(() => goToView(this.dataset.uri, "view"));
        } catch(err) { 
          this.uploadError = err.response;
          this.distrStatus = STATUS_FAILED;
        }
      },   

      processAutocompleteMenu () {
        return processAutocompleteMenu();
      }, 
  
      resolveEntityAuthor (query) {
        this.items = axios.get('/',{params:{view:'resolve',term:query+"*", type: "http://xmlns.com/foaf/0.1/Person"},
                             responseType:'json' })
            .then(function(response) {
              console.log(response.data)
                return response.data;
            });
      },
      resolveEntityInstitution (query) {
        this.items = axios.get('/',{params:{view:'resolve',term:query+"*", type:"http://xmlns.com/foaf/0.1/Organization"},
                             responseType:'json' })
            .then(function(response) {
              console.log(response.data)
                return response.data;
            });
      },
      // selectedAuthorChange(item) {
      //   console.log(`selected item ${item}`)
      //     // window.location.href = '/'+'about?uri='+window.encodeURIComponent(item.node);
      // }, 



    showNewInstitution () {
      EventServices.$emit('open-new-instance', {status: true, title:"Add new institution", type: "institution"});
      return
    },
    showNewAuthor () {
      EventServices.$emit('open-new-instance', {status: true, title:"Add new author", type: "author"});
      return
    },
    newChart(){
    return EventServices.navTo("new", true)
    },
    cancelFilter(){
    return EventServices.cancelChartFilter();
    }
}, 

created() { 
  this.loading = true;
  if(EventServices.authUser == undefined){
      return this.loading=false;
  } 
  this.loadDataset();
  EventServices
  .$on('isauthenticated', (data) => this.authenticated = data)
  .$on('institutionsupdated', (data) => this.availableInstitutions = data)
  .$on('authorsupdated', (data) => this.availableAuthors = data)
}
})