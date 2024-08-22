import Vue from 'vue';
import uuidv4 from "uuid";
import { EventServices } from '../../../../modules';
import VueMaterial from "vue-material";
import { getDefaultDataset, loadDataset, saveDataset, deleteDataset, saveDistribution, saveImg, getDoi, getDatasetAuthor} from "../../../../utilities/dataset-upload";
import lookupOrcid from "../../../../utilities/orcid-lookup";
import {processAutocompleteMenu, getAuthorList, getOrganizationlist} from "../../../../utilities/autocomplete-menu"
import { goToView } from "../../../../utilities/views"; 
Vue.use(VueMaterial);


const STATUS_INITIAL = 0, STATUS_SAVING = 1, STATUS_SUCCESS = 2, STATUS_FAILED = 3;
const datasetId = uuidv4(); 


export default Vue.component('dataset-uploader', {
    props: [
	'datasetType'
    ],
data() {
    return {
      dataset: {
	"@type": this.datasetType,
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
	    this.dataset['@type'] = this.datasetType;
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
          curFile['label'] = this.createDefaultLabel(curFile.name);
          this.uploadedFiles.push( curFile );
        }
      } 
    }, 
    /* 
      Helper to generate a default rdfs:label for distributions
    */
    createDefaultLabel(fileName){
      var fileNameSplit = fileName.split(".");  
      fileNameSplit.pop();
      var rejoined = fileNameSplit.join(".");
      var underscore2Space = rejoined.replace(/_/g, ' ');
      return underscore2Space.replace(/[^a-zA-Z0-9]+/g, " ").trim();
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
      this.distrStatus = STATUS_SAVING; 

      // If there are no files, cancel
      if (!fileList.length) {return this.distrStatus = STATUS_INITIAL}; 

      await saveDistribution(fileList, this.generatedUUID)
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
      this.depictStatus = STATUS_SAVING; 

      // If there are no images, cancel
      if (!fileList.length){return this.depictStatus = STATUS_INITIAL} 

      await saveImg(fileList[0], this.generatedUUID)
      .then(urls => {   
        this.dataset.depiction.accessURL = urls[1];
        this.dataset.depiction['@id'] = urls[0];
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

    async resolveEntityAuthor(query){
      this.autocomplete.availableAuthors = await getAuthorList(query);
    },

    async resolveEntityInstitution (query) {
      this.autocomplete.availableInstitutions = await getOrganizationlist(query);
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
        this.contributors.push({
          '@id': agent['@id'], 
          "name": agent.name,
          onbehalfof: {
            "name": null,
          },
        }); 
    },

    async getDOI() {
      // Don't do anything if no doi has been entered
      if (this.doi === ""){
        return
      }
      // Otherwise use the describe view
      const response = await getDoi(this.doi);
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
      const doiAuth = await getDatasetAuthor(authorId);
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
      }
      if ('prov:specializationOf' in doiAuth){
        newAuthor['specializationOf'] = {};
        newAuthor['specializationOf']['@id'] = doiAuth['prov:specializationOf']['@id'];
      }
      this.contributors.push(newAuthor)
      return newAuthor;
    },

    async lookupOrcid(){
      this.cpIDError = false;
      const response = await lookupOrcid(this.cpID, "contactPoint")
      .then(response => {
        let orcidData = response;
        if (orcidData === "Invalid"){
          return this.resetContactPoint();
        }
        else{
          // Assign values as available
          if ('schema:familyName' in orcidData){
            this.dataset.contactpoint.cplastname = orcidData['schema:familyName']
          }
          if ('schema:givenName' in orcidData){
            this.dataset.contactpoint.cpfirstname = orcidData['schema:givenName']
          }
        }
      })
      .catch(err => { 
        throw err;
      }); 
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
      return processAutocompleteMenu(param)
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
