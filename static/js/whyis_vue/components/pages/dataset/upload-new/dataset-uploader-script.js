import Vue from 'vue';
import { EventServices } from '../../../../modules';
import VueMaterial from "vue-material";
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
        depiction: {
          name: '',
          accessURL: null,
          '@id': null,
          hasContent: null,
        }
      },

      generatedUUID: datasetId,

      doi: "",
      doiLoading: false,
      cpID: "",
      cpIDError: false,
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
      distrStatus: STATUS_INITIAL,
      depictStatus: STATUS_INITIAL,
      isInvalidUpload: false,
      isInvalidForm: false,

      authenticated: EventServices.authUser,
      autocomplete: {
        availableInstitutions: [],
        availableAuthors: [],
      },
      loading: false,
      loadingText: "Loading Existing Datasets",

      /// search
      query: null,
      selectedAuthor: [],

      // TODO: deal with empty orgs
      selectedOrg: [],
      editableOrgs: true,
    }
},
methods: {


    loadDataset () {
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

    dateFormat(value, event) {
      return moment(value).format("YYYY-MM-DD");
    },
    removeElement: function (index) {
      this.contributors.splice(index, 1);
    },
    
    editDois: function () {
      if (this.doi !== ""){
        this.dataset.refby = "https://dx.doi.org/" + this.doi;
      }
    },

    /* 
      Contributor and author handling: User facing 
    */
    handleContrAuth: function(){
      for (var index in this.contributors){
        let author = this.contributors[index];
        let newAuthor = {
          '@id': author['@id'],
          "@type": "person",
          "name": author['name'],
        }
        if ((author.onbehalfof.name !== null) && (author.onbehalfof.name !== undefined)){
          newAuthor["onbehalfof"] = {
            "@id": author.onbehalfof['@id'],
            "@type": "organization",
            "name": author.onbehalfof.name,
          }
        }
        if ('specializationOf' in author){
          newAuthor["specializationOf"] = {
                "@id": author['specializationOf']['@id']
          }
        }
        this.dataset.author.push(newAuthor);
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

      //TODO: Move this to dataset-upload.js

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

      // TODO: move this to dataset-upload.js
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
      this.doiLoading = true;
      // Check for at least one distribution
      if (!this.uploadedFiles.length){
        this.isInvalidUpload = true;
        this.doiLoading = false;
      } else { 
        this.saveRepImg(); 
        this.saveDistribution(); 
        
        if (this.doi === ""){
          this.doiLoading = false;
          this.setDone('first', 'second');
        }
        else {
          const result = await this.getDOI();
        }
      }
    },

    checkSecondPage(){
      // Check the required fields
      const titleBool = (this.dataset.title === "");
      const cpidBool = ((this.cpID === null) || (this.cpID === ""));
      const cpfirstnameBool = (this.dataset.contactpoint.cpfirstname === "");
      const cplastnameBool = (this.dataset.contactpoint.cplastname === "");
      const cpemailBool = (this.dataset.contactpoint.cpemail === "");
      const descriptionBool = (this.dataset.description === "");

      // Prevent form submission if required fields are empty
      if (titleBool || cpidBool || cpfirstnameBool || cplastnameBool || cpemailBool || descriptionBool){
        this.isInvalidForm = true;
      } else if (!this.validEmail(this.dataset.contactpoint.cpemail)) { 
        this.dataset.contactpoint.cpemail = '';
        this.isInvalidForm = true;
      } else { 
        this.isInvalidForm = false;
        this.dataset.contactpoint['@id'] = `http://orcid.org/${this.cpID}`;
        this.dataset.contactpoint.name = this.dataset.contactpoint.cpfirstname.concat(" ", this.dataset.contactpoint.cplastname);
        this.setDone('second', 'third'); 
        this.handleContrAuth();
        this.editDois();
      }
    },

    // Handle steppers
    setDone (id, index) {
      this[id] = true; 
      if (index) {
        this.active = index;
      };
    },
    
    // Use regex for valid email format
    validEmail (email) {
      var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    },

    // Submit and post as nanopublication
    submitForm: function () {
      try { 
        saveDataset(this.dataset, this.generatedUUID) 
        .then(() => goToView(this.dataset.uri, "view"));
      } catch(err) { 
        this.uploadError = err.response;
        this.distrStatus = STATUS_FAILED;
      }
    },  

    // Auto-complete methods for author and institution
    resolveEntityAuthor (query) { 
      // Until the resolver allows for OR operator, must run two gets to capture both person types
      axios.all([
        axios.get(
          `/?term=${query}*&view=resolve&type=http://xmlns.com/foaf/0.1/Person`),
        axios.get(
          `/?term=${query}*&view=resolve&type=http://schema.org/Person`)
      ])
      .then(axios.spread((foafRes, schemaRes) => {
        // Merge the results and sort by score descending
        this.autocomplete.availableAuthors = foafRes.data.concat(schemaRes.data)
        .sort((a, b) => (a.score < b.score) ? 1 : -1);
      }))
      .catch((err) => {
        throw(err)
      });
    },
    resolveEntityInstitution (query) {
      this.autocomplete.availableInstitutions = axios.get(
        `/?term=${query}*&view=resolve&type=http://schema.org/Organization`)
          .then(function(response) {
            // console.log(response.data);
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
      this.contributors.push({
        '@id': item.node, 
        "name": name,
        onbehalfof: {
          "name": null,
        },
      });
      this.selectedAuthor = "";
      // console.log(this.contributors)
    }, 
    selectedOrgChange(row, event){
      var currentOrg = this.contributors[row]['onbehalfof'];
      currentOrg['name'] = event.label;
      currentOrg['@id'] = event.node;
      return event.label;
    },

    //TODO: decide how to deal with not having organizations available
    addAuthor (agent) {
      var elem = document.createElement("tr");

      // if (arguments.length === 1) {
      //   this.contributors.push(agent);
      // } else {
        this.contributors.push({
          '@id': agent['@id'], 
          "name": agent.name,
          // "firstname": "",
          // "lastname": "",
          onbehalfof: {
            "name": null,
          },
        }); 
      // }
      
      // console.log(this.contributors)
    },

    async getDOI() {
      // Don't do anything if no doi has been entered
      if (this.doi === ""){
        return
      }

      // Otherwise use the describe view
      const response = await axios.get(`/doi/${this.doi}?view=describe`, {
        headers: {
          'Accept': 'application/json',
        }
      });
      const result = await this.useDescribedDoi(response, this.doi)
      .then(response => { 
        this.doiLoading = false;
        this.setDone('first', 'second');
      })
      .catch(err => {  
        this.doiLoading = false;
        this.setDone('first', 'second');
        throw err;
      }); 
    }, 

    // Fill the form with available data from doi
    async useDescribedDoi (response, doi){
      const doiData = response.data['@graph'];
      for (var index in doiData){
        let entry = doiData[index]
        if (entry['@id'] == `http://dx.doi.org/${doi}`){
          if ('dc:title' in entry){
            this.dataset.title = entry['dc:title']
          }
          if ('dc:date' in entry){
            this.dataset.datemod['@value'] = entry['dc:date']['@value'];
            this.dataset.datepub['@value'] = entry['dc:date']['@value'];
          }
          if ('dc:creator' in entry){
            for (var author in entry['dc:creator']){
              await this.getAuthorDescribed(entry['dc:creator'][author]['@id'])
            }
          }
        }      
      }
    },

    async getAuthorDescribed(authorId){ 
      // Use describe view on listed authors
      const response = await axios.get(`/about?uri=${authorId}&view=describe`, {
        headers: {
          'Accept': 'application/json',
        }
      })
      .then(async response => { 
        let doiAuth = response.data
        if ('@graph' in response.data){
          for (var entry in response.data['@graph']){
            if (response.data['@graph'][entry]['@id'] === authorId){
              doiAuth = response.data['@graph'][entry]
            }
          }
        }
        var newAuthor = {
          '@id': doiAuth['@id'],
          name: doiAuth['foaf:name'],
          onbehalfof: {
            name: null,
          },
        }
        if ('owl:sameAs' in doiAuth){
          newAuthor['specializationOf'] = {};
          newAuthor['specializationOf']['@id'] = doiAuth['owl:sameAs']['@id'];
          await this.getAuthorOrcid(newAuthor['specializationOf']['@id']);
        }
        if ('prov:specializationOf' in doiAuth){
          newAuthor['specializationOf'] = {};
          newAuthor['specializationOf']['@id'] = doiAuth['prov:specializationOf']['@id'];
          // newAuthor['onbehalfof']['name'] = await this.getAuthorOrcid(newAuthor['specializationOf']['@id']);
          // console.log(affiliation)
        }
        this.contributors.push(newAuthor)
        // console.log(this.contributors)
        return newAuthor;
      })
      .catch(err => { 
        throw err;
      }); 
    },

    async getAuthorOrcid(authorOrcidUri){
      var authorOrcid = authorOrcidUri.substring(authorOrcidUri.lastIndexOf("/") + 1, authorOrcidUri.length);;
      await axios.get(`/orcid/${authorOrcid}?view=describe`, {
        headers: {
          'Accept': 'application/json',
        }
      })
      .then(async response => { 
        let orcidAuth = response.data
        // Sometimes there are multiple entries in the graph, find the right one
        orcidAuth = this.findCorrectEntry(orcidAuth, `http://orcid.org/${authorOrcid}`)
        // Assign values as available
        if ('schema:affiliation' in orcidAuth){
          var affiliationResponse = await axios.get(`/about?uri=${orcidAuth['schema:affiliation']['@id']}&view=describe`, {
            headers: {
              'Accept': 'application/json',
            }
          })
          var affiliation = affiliationResponse.data;
          affiliation = this.findCorrectEntry(affiliation, orcidAuth['schema:affiliation']['@id']);
          return affiliation['schema:name']
        }
      })
      .catch(err => { 
        throw err;
      }); 
    },

    findCorrectEntry(responseData, correctId){
      if ('@graph' in responseData){
        // If invalid id, graph will be empty so return nothing
        if (!responseData['@graph'].length){
          return
        }
        // Look for the entry that corresponds to the actual id
        for (var entry in responseData['@graph']){
          if (responseData['@graph'][entry]['@id'] === correctId){
            return responseData['@graph'][entry]
          }
        }
      }
    },

    async lookupOrcid(){
      this.cpIDError = false;
      // Check for valid ORCID id format
      const regUnhyphenated = /^\d{16}$/
      const unhyphenated = regUnhyphenated.test(this.cpID);
      if (unhyphenated){
        this.cpID = this.cpID.replace(/^\(?([0-9]{4})\)?([0-9]{4})?([0-9]{4})?([0-9]{4})$/, "$1-$2-$3-$4")
      }
      const regHyphenated = /^\(?([0-9]{4})\)?[-]?([0-9]{4})[-]?([0-9]{4})[-]?([0-9]{4})$/;
      const validOrcid = regHyphenated.test(this.cpID);

      // Get the data for this ORCID id through Whyis using view=describe
      if (validOrcid){
        const response = await axios.get(`/orcid/${this.cpID}?view=describe`, {
          headers: {
            'Accept': 'application/ld+json',
          }
        })
        .then(response => { 
          let orcidAuth = response.data
          // Sometimes there are multiple entries in the graph
          if ('@graph' in response.data){
            // If invalid ORCID, graph will be empty so return nothing
            if (!response.data['@graph'].length){
              return this.resetContactPoint();
            }
            // Look for the entry that corresponds to the actual ORCID id
            for (var entry in response.data['@graph']){
              if (response.data['@graph'][entry]['@id'] === `http://orcid.org/${this.cpID}`){
                orcidAuth = response.data['@graph'][entry]
              }
            }
          }
          // Assign values as available
          if ('schema:familyName' in orcidAuth){
            this.dataset.contactpoint.cplastname = orcidAuth['schema:familyName']
          }
          if ('schema:givenName' in orcidAuth){
            this.dataset.contactpoint.cpfirstname = orcidAuth['schema:givenName']
          }
        })
        .catch(err => { 
          throw err;
        }); 
      }
      else {
        // Invalid ORCID id
        return this.resetContactPoint();
      }
    },

    // Clear contact point values
    resetContactPoint(){
      this.cpIDError = true;
      this.dataset.contactpoint.cplastname = "";
      this.dataset.contactpoint.cpfirstname = "";
    },

    // Create dialog boxes
    showNewInstitution () {
      EventServices
      .$emit('open-new-instance', {status: true, title:"Add new institution", type: "organization"})
      return
    },
    showNewAuthor () {
      EventServices
      .$emit('open-new-instance', {status: true, title:"Add new author", type: "author"})
      .$on('authorSelected', (data) => this.addAuthor(data) );
      return
    },

    // Modify styling of menu to override bad width
    setListStyle(param){
      var runSetStyle;
      if(param){
        if(runSetStyle){
          return clearInterval(runSetStyle);
        }
      }
      runSetStyle = setInterval(() => {
        const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
        if(itemListContainer.length >= 1) {
          // console.log(itemListContainer[0].parentNode.nodeName)
          itemListContainer[0].setAttribute("style", "width: 90%; max-width: 90%; position: absolute; top: 841px; left: 95px; will-change: top, left;")
          return status = true
        }
      }, 20)
      return runSetStyle
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
}
})
