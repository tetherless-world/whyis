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


export default Vue.component('dataset-uploader', {
data() {
    return {
      dataset: { 
        title: "",
        description: "",
        contactpoint: {
          "@type": "individual",
          "@id": null,
          name: "",
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
        // distribution:{
        //   accessURL: null,
        //   '@id': null,
        //   hasContent: null,
        // },
        depiction: {
          name: '',
          accessURL: null,
          '@id': null,
          hasContent: null,
        }
      },

      generatedUUID: datasetId,

      //TODO: remove dois
      doi: "",
      dois: "",
      contributors: [],
      contributors2: [],
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

      // TODO: Switch author and org
      authorFirst: true,
      selectedOrg: [],
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
    //TODO
    removeElement2: function (index) {
      this.contributors2.splice(index, 1);
    },
    //TODO for doi autofill: replaced multiple with only one
    editDois: function () {
      this.dataset.refby = "https://dx.doi.org/" + this.doi;
      // var doisseparated = this.dois.split(/[ ,]+/);
      // this.dataset.refby = doisseparated.map((x) => "https://dx.doi.org/" + x);
    },

    /* 
      Contributor and author handling: User facing 
    */
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
    handleContrAuth2: function(){
      this.dataset.author = this.contributors2
      this.dataset.contributor = []
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
      this.selectedAuthor = [];
      // console.log(this.contributors)
    },
    removeAuthor (ind, index){
      this.contributors[index]['authors'].splice(ind, 1)
      this.selectedAuthor[index] = "";
      // console.log(this.contributors)
    },
    //TODO: 
    selectOrganization (index){
      if ((this.selectedOrg[index] !== null)&& (this.selectedOrg[index] !== "")){
        this.contributors[index]['onbehalfof'].push( 
          {
            "@type": "organization",
            name: this.selectedOrg[index],
          },
        );
      }
    },

    /*
      Distribution and representation handling: server
    */
    handleDistrUpload(files) { 
      let uploadedFiles = files;  
      // Adds the uploaded file to the files array
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

      // If there are no files, cancel
      if (!fileList.length) {return this.distrStatus = STATUS_INITIAL}; 

      // Specify is a dataset so handles multiple files
      distrData.append('upload_type', 'http://www.w3.org/ns/dcat#Dataset')

      // append the files to FormData
      Array
        .from(Array(fileList.length).keys())
        .map(x => {
          distrData.append(fileList[x].name, fileList[x]); 
        });

      // Where to save the distribution
      const uri = `${lodPrefix}/dataset/${this.generatedUUID}`;
      const baseUrl = `${window.location.origin}/about?uri=${uri}`;
      this.distrStatus = STATUS_SAVING; 

      axios.post( baseUrl,
          distrData,
          {
            headers: {
                'Content-Type': 'multipart/form-data',
            }, 
          }
      )
      .then(x => {
        this.distrStatus = STATUS_SUCCESS; 
      })
      .catch(err => { 
        this.uploadError = err.response;
        this.distrStatus = STATUS_FAILED;
      });
    }, 

    async saveRepImg() {
      const fileList = this.uploadedImg; 
      // Where to save the image
      const uri = `${lodPrefix}/dataset/${this.generatedUUID}/depiction`;
      const baseUrl = `${window.location.origin}/about?uri=${uri}`
      this.depictStatus = STATUS_SAVING; 

      // If there are no images, cancel
      if (!fileList.length){return this.depictStatus = STATUS_INITIAL} 

      let form = new FormData();
      form.append('upload_type', 'http://purl.org/net/provenance/ns#File')
      form.append('depiction', fileList[0]) 

      var data = {
        '@id': uri,
        'file': form,
      }
      
      await fetch(baseUrl, {
        method: 'POST',
        body: data, 
        headers: {
            Accept: 'application/json',
            'Content-Type': 'multipart/form-data', 
        }, 
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

    // Load a thumbnail of the representative image
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

    async checkFirstPage(){ 
      // Check for at least one distribution
      // if (!this.uploadedFiles.length){
      //   this.isInvalidUpload = true;
      // } else { 
        this.saveRepImg(); 
        this.saveDistribution(); 

        const result = await this.getDOI()
        .then(this.setDone('first', 'second'));
      // }
    },

    checkSecondPage(){
      // Check the required fields
      const titleBool = (this.dataset.title === "");
      const cpidBool = (this.dataset.contactpoint['@id'] === null);
      const cpfirstnameBool = (this.dataset.contactpoint.cpfirstname === "");
      const cplastnameBool = (this.dataset.contactpoint.cplastname === "");
      const cpemailBool = (this.dataset.contactpoint.cpemail === "");
      const descriptionBool = (this.dataset.description === "");

      // Prevent form submission if required fields are empty
      if (titleBool || cpidBool || cpfirstnameBool || cplastnameBool || cpemailBool || descriptionBool){
        this.isInvalidForm = true;
      } if (!this.validEmail(this.dataset.contactpoint.cpemail)) { 
        this.dataset.contactpoint.cpemail = '';
        this.isInvalidForm = true;
      } else { 
        this.isInvalidForm = false;
        this.dataset.contactpoint.name = this.dataset.contactpoint.cpfirstname.concat(" ", this.dataset.contactpoint.cplastname);
        this.setDone('second', 'third'); 
        if(this.authorFirst){
          this.handleContrAuth2();
        } else{
          this.handleContrAuth();
        }
        this.editDois();
      }
    },

    // Use regex for valid email format
    validEmail (email) {
      var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    },

    // Handle steppers
    setDone (id, index) {
      this[id] = true; 
      if (index) {
        this.active = index;
      };
    },

    submitForm: function () {
      try { 
        saveDataset(this.dataset, this.generatedUUID) 
        .then(() => goToView(this.dataset.uri, "view"));
      } catch(err) { 
        this.uploadError = err.response;
        this.distrStatus = STATUS_FAILED;
      }
    },   

    // processAutocompleteMenu () {
    //   return processAutocompleteMenu();
    // }, 

    // Auto-complete methods for author and institution
    resolveEntityAuthor (query) {
      this.autocomplete.availableAuthors = axios.get('/',
        {params:{view:'resolve',term:query+"*", type: "http://xmlns.com/foaf/0.1/Person"}, responseType:'json' })
          .then(function(response) {
            console.log(response.data);
            return response.data;
          });
    },
    resolveEntityInstitution (query) {
      this.autocomplete.availableInstitutions = axios.get('/',
      {params:{view:'resolve',term:query+"*", type:"http://xmlns.com/foaf/0.1/Organization"}, responseType:'json' })
          .then(function(response) {
            console.log(response.data);
            return response.data;
          });
    },
    selectedAuthorChange(item) {
      var elem = document.createElement("tr");
      var name;
      if (item.label){
        name = item.label;
      }
      else{
        name = item.name;
      }
      this.contributors2.push({
        '@id': item.node, 
        "@type": "person",
        "name": name,
        onbehalfof: {
          "@type": "organization",
          "name": "N/A"
        },
      });
      console.log(this.contributors2)
    }, 

    //TODO
    addAuthor (agent) {
      var elem = document.createElement("tr");

      // if (arguments.length === 1) {
      //   this.contributors2.push(agent);
      // } else {
        this.contributors2.push({
          '@id': agent['@id'], 
          "@type": "person",
          "name": agent.name,
          // "firstname": "",
          // "lastname": "",
          onbehalfof: {
            "@type": "organization",
            "name": "N/A"
          },
        }); 
      // }
      
      console.log(this.contributors2)
    },

    async getDOI() {
      // Don't do anything if no doi has been entered
      if (this.doi === ""){
        return
      }
      //Otherwise... 
      const datasetTitle = this.dataset.title;
      const res = await axios.get(`http://dx.doi.org/${this.doi}`, {
        headers: {
          'Accept': 'application/json',
        }
      })
      .then(async response => {
        console.log(response.data); 
        this.dataset.title = response.data.title;
        if (response.data.abstract){
          this.dataset.description = response.data.abstract;
        }
        var dateiss = response.data.issued;
        if (dateiss){
          if (dateiss['date-parts']){
            var dateissstring = dateiss['date-parts'].toString();
            this.dataset.datepub['@value'] = await this.checkDateFormat(dateissstring);
          }
        }
        var datecreated = response.data.created;
        if (datecreated){
          if (datecreated['date-parts']){
            var datecreatedstring = datecreated['date-parts'].toString();
            this.dataset.datemod['@value'] = await this.checkDateFormat(datecreatedstring);
          }
        }
        //// TODO : Fix this
        // if (response.data.author){
        //   response.data.author.forEach(element => {
        //     this.getAuthorFromDOI(element);
        //   });
        // }
      })
      .catch(err => { 
        throw err;
      }); 
    }, 

    async checkDateFormat (date) {
      date = date.replace(/,/g, "-");
      const incDateRegExp = /^[0-9]{4}\-[0-9]{1}\-[0-9]{2}?$/;
      if(incDateRegExp.test(date)){
        date = date.substring(0, 5) + '0' + date.substring(5)
      }
      return date
    },

    getAuthorFromDOI(author){
      var newAuthor = {
        '@id': null,
        name: "",
        onbehalfof: null,
      }
      if (author.ORCID){
        newAuthor['@id'] = author.ORCID;
      }
      if (author.family && author.given){
        newAuthor.name = author.given + " " + author.family;
        this.contributors2.push(newAuthor)
      } else if (author.name){
        newAuthor.name = author.name;
        this.contributors2.push(newAuthor)
      }
    },

    // Create dialog boxes
    showNewInstitution () {
      EventServices
      .$emit('open-new-instance', {status: true, title:"Add new institution", type: "institution"})
      return
    },
    showNewAuthor () {
      EventServices
      .$emit('open-new-instance', {status: true, title:"Add new author", type: "author"})
      .$on('authorSelected', (data) => this.addAuthor(data) );
      return
    },

    // Unused, relates to speed dials
    newChart(){
    return EventServices.navTo("new", true)
    },
    cancelFilter(){
    return EventServices.cancelChartFilter();
    }
}, 

created() { 
  this.loading = true;
  // Make sure user is authenticated
  if(EventServices.authUser == undefined){
      return this.loading=false;
  } 
  this.loadDataset();
  EventServices
  .$on('isauthenticated', (data) => this.authenticated = data)
  // .$on('institutionsupdated', (data) => this.availableInstitutions = data)
  // .$on('authorsupdated', (data) => this.availableAuthors = data)
}
})
