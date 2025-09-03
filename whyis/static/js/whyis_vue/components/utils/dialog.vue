<template>
  <div>
    <!-- Bootstrap Modal -->
    <div class="modal fade" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          
          <!-- Intro Modal Content -->
          <div class="viz-intro" v-if="dialog.intro">
            <div class="modal-header">
              <h5 class="modal-title">Tips</h5>
              <button type="button" class="btn-close" @click="cancelDel" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <intros :screen="introTipScreen" />
            </div>
            <div class="modal-footer justify-content-between">
              <button type="button" class="btn btn-outline-secondary" @click.prevent="cancelDel" v-if="introTipScreen == 1">Skip</button>
              <button type="button" class="btn btn-outline-secondary" @click.prevent="previousScreen" v-else>Previous</button>
              <div>
                <button type="button" class="btn btn-primary" @click.prevent="nextScreen" v-if="introTipScreen <= 3">Next</button>
                <button type="button" class="btn btn-primary" @click.prevent="cancelDel" v-else>Close</button>
              </div>
            </div>
          </div>

          <!-- Regular Modal Content -->
          <div v-else>
            <div class="modal-header utility-dialog-box_header">
              <h5 class="modal-title" v-if="dialog.status">{{ dialog.title }}</h5>
              <h5 class="modal-title" v-else-if="makeNew.status">{{ loginRequestSent? "Login" : makeNew.title }}</h5>
              <h5 class="modal-title" v-else>{{ loginRequestSent? "Login" : "Filter Chart" }}</h5>
              <button type="button" class="btn-close" @click="cancelDel" aria-label="Close"></button>
            </div>

            <div class="modal-body utility-dialog-box_login">
              <div v-if="dialog.share" class="mb-3">
                <div class="form-floating">
                  <textarea class="form-control" id="sharedlinktext" v-model="dialog.chart" style="height: 100px" maxlength="150">{{ dialog.chart }}</textarea>
                  <label for="sharedlinktext">Chart Link</label>
                </div>
                <small class="text-muted">{{ dialog.message }}</small>
              </div>
              
              <div v-else-if="dialog.tableview" class="mb-3">
                <div class="viz-intro-query" style="min-height: 40rem !important">
                  <yasr v-bind:results="dialog.tableview"></yasr>
                </div>
              </div>
              
              <div v-else-if="dialog.query" class="mb-3">
                <div class="viz-intro-query">
                  <yasqe v-model="dialog.query" :showBtns='true'></yasqe>
                </div>
                <small class="text-muted">{{ dialog.message }}</small>
              </div>
              
              <div v-else class="mb-3">
                <p>{{ dialog.message }}</p>
              </div>
            </div>

            <div class="modal-footer" v-if="dialog.share || dialog.delete || dialog.query || dialog.diag || dialog.tableview">
              <div v-if="dialog.share || dialog.query || dialog.tableview">
                <button type="button" class="btn btn-secondary" @click.prevent="cancelDel">Close</button>
              </div>
              <div v-else-if="dialog.delete || dialog.diag">
                <button type="button" class="btn btn-secondary" @click.prevent="cancelDel">Close</button>
                <button type="button" class="btn btn-primary ms-2" @click.prevent="dialogAction" v-if="!dialog.btn">{{dialog.title}}</button>
            </div>
          </div>
        </div>

        <div class="utility-dialog-box_login" v-else-if="makeNew.status">
          <md-field v-if="makeNew.type === 'organization'">
              <label>Name of Organization</label>
              <md-input v-model="organization.name"></md-input>
          </md-field>

          <div v-else-if="makeNew.type === 'author'" >
            <div class="md-layout md-gutter" style="align-items: center; justify-content:center">  
              <div class="md-layout-item md-size-50">
                <md-field>
                  <label>Name</label>
                  <md-input v-model="author.name" required=""></md-input> 
                </md-field>
              </div> 
              <div class="md-layout-item md-size-50">
                <md-field>
                  <label>ORCID Identifier</label>
                  <md-input v-model="author['@id']" style="max-width: 100%" required></md-input> 
                </md-field>
              </div> 
            </div>
            <div style="margin-bottom: 40px; text-align: center;">
              Don't have an ORCID iD?
              <a href="https://orcid.org/" target="_blank">Create one here</a>
            </div>
          </div>
          
          <div class="utility-margin-big viz-2-col">
            <div class="utility-align--right utility-margin-top"> 
            </div>
            <div class="utility-align--right utility-margin-top">
              <a @click.prevent="onCancel" class="btn-text btn-text--default"> &larr; Exit</a> &nbsp; &nbsp;
              <a @click.prevent="onSubmitNew" class="btn-text btn-text--default">Submit &rarr; </a>
            </div>
          </div>
        </div>

        <div class="utility-dialog-box_login" v-else>
          <div class="md-layout-item">
            <md-field>
              <label for="movie">Filter By</label>
              <md-select v-model="filterby" name="filterby" id="filterby" placeholder="Filter By">
                <md-option value="title">Chart Title</md-option>
                <md-option value="query">Chart Query</md-option>
                <md-option value="description">Chart Description</md-option>
              </md-select>
            </md-field>
          </div>
          <md-autocomplete v-model="selectedText" :md-options="filterby == 'title' ? chartResults.title: filterby == 'query' ? chartResults.query : chartResults.description" :md-open-on-focus="false">
            <label>Filter Keyword</label>

            <template slot="md-autocomplete-item" slot-scope="{ item, term }">
              <md-highlight-text :md-term="term">{{ item }}</md-highlight-text>
            </template>

            <template slot="md-autocomplete-empty" slot-scope="{ term }">
              No {{ filterby }} matching "{{ term }}" were found.
            </template>
          </md-autocomplete>
          <div class="utility-margin-big viz-2-col">
            <div class="utility-align--right utility-margin-top">
              
            </div>
            <div class="utility-align--right utility-margin-top">
              <a @click.prevent="onCancel" class="btn-text btn-text--default"> &larr; Exit</a> &nbsp; &nbsp;
              <a @click.prevent="onConfirm" class="btn-text btn-text--default">Filter &rarr; </a>
            </div>
          </div>
        </div>
      </div>

    </md-dialog>
  </div>
</template>
<style lang="scss" src="../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import EventServices from '../../modules/events/event-services'
  import { processFloatList, resetProcessFloatList } from '../../utilities/dialog-box-adjust'
  import { goToView } from '../../utilities/views'
  import { lookupOrcid } from '../../utilities/orcid-lookup'
  export default Vue.component('dialogBox', {
    data () {
      return {
        active: false,
        required: null,
        hasMessages: false,
        loginRequestSent: false,
        filterby: "title",
        selectedText: null,
        password: null,
        introTipScreen: 1,
        textarea: null,
        chartResults: {
          title: [],
          description: [],
          query:[],
          tableview: []
        },
        dialog:{
          status: false
        },
        makeNew:{
          status: false
        },
        agent: "",
        organization:{
          type: "Organization",
          name: "", 
        },
        author:{
          type: "Person",
          name: "",
          '@id': null,
        }
      }
    },
    computed: {
      messageClass () {
        return {
          'md-invalid': this.hasMessages
        }
      },
    },
    watch: {
      dialog(newValue, OldValue){
        if(newValue && newValue.share){
          this.copyText()
        }
      }
    },
    components: {
    },
    destroy(){
        return resetProcessFloatList();
    },
    methods: {
      copyText(){
        setTimeout(()=>{
          const text = document.getElementById('sharedlinktext')
          if(text){
            text.select();
            text.setSelectionRange(0, 99999); //the range here, is used to target mobile devices
            document.execCommand("copy");
            return EventServices.$emit('snacks', {status:true, message: "Chart link copied!", tip: "Paste Anywhere"})
          }
        },800)
      },
      onConfirm() {
        this.active = !this.active
        this.loginRequestSent = false
        EventServices.$emit('close-filter-box', this.active)
        return EventServices.filterChart(this.filterby, this.selectedText)
      },
      onSubmitNew(){
        this.active = !this.active
        this.loginRequestSent = false
        if (this.agent === "author"){
          const author = lookupOrcid(this.author['@id'], "author") 
          console.log(author)
        } else if (this.agent === "organization"){
          // saveAgent(this.organization)
          return
        }
        EventServices.$emit('close-filter-box', this.active)
          // // reset this.author
          // this.author.name = "";
          // this.author['@id'] = null;
        return
      },
      onCancel() {
        this.active = !this.active
        EventServices.$emit('close-filter-box', this.active)
        
      },
      cancelDel(){
        this.active = !this.active
        this.dialog = { status: false}
        EventServices.$emit('close-filter-box', this.active)
      },
      dialogAction(){
        this.active = !this.active
        if(this.dialog.delete){
          EventServices.deleteAChart(this.dialog.chart)
        } else if(this.dialog.reset) {
          EventServices.resetChart()
        } 
        this.dialog = { status: false}
        return EventServices.$emit('close-filter-box', this.active)
      },
      nextScreen(){
        return this.introTipScreen += 1
      },
      previousScreen(){
        if(this.introTipScreen >= 2){
          return this.introTipScreen -= 1
        }
        return;
      }
    },
    created() {
      EventServices
      .$on('open-filter-box', (data) => {
        if(data.type == "filter") {
          this.active = data.open
          return processFloatList()
        } else {
          this.active = data.open
          this.loginRequestSent = true
        }
      }).$on("appstate", (data) => {
        if(data.length >= 1){
          this.chartResults.title = data.map(el => el.backup.title)
          this.chartResults.description = data.map(el => el.backup.description)
          this.chartResults.query = data.map(el => el.backup.query)
        }
      }).$on("dialoguebox", (data) => {
        if(data && data.intro){
          this.active = data.status
          this.dialog = data
          this.introTipScreen = 1
        } else {
          this.active = data.status
          this.dialog = data
        }
      }).$on('open-new-instance', (data) => {
        this.active = data.status
        this.agent = data.type
        this.makeNew = data
      })
    }
  })
</script>