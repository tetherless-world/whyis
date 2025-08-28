<template>
  <div>
    <md-dialog :md-active.sync="active" :md-click-outside-to-close="true">
      <div class="viz-intro" v-if="dialog.intro">
        <div class="utility-gridicon utility-margin-top"><span class="viz-intro-title">tips &dot;</span></div>
        <intros :screen="introTipScreen" />
        <div class="utility-align--right">
          <a @click.prevent="cancelDel" class="btn-text btn-text--primary btn--animated utility-margin-right" v-if="introTipScreen == 1"><span class="md-title"> Skip</span></a>
          <a @click.prevent="previousScreen" class="btn-text btn-text--primary btn--animated utility-margin-right" v-else><span class="md-title">Previous</span></a>
          <a @click.prevent="nextScreen" class="btn-text btn-text--primary btn--animated" v-if="introTipScreen <= 3"><span class="md-title">Next</span></a>
          <a @click.prevent="cancelDel" class="btn-text btn-text--primary btn--animated" v-else><span class="md-title">Close</span></a>
        </div>
      </div>

      <div v-else>
        <div class="utility-dialog-box_header" >
          <md-dialog-title v-if="dialog.status">{{ dialog.title }}</md-dialog-title>
          <md-dialog-title v-else-if="makeNew.status">{{ loginRequestSent? "Login" : makeNew.title }}</md-dialog-title>
          <md-dialog-title v-else>{{ loginRequestSent? "Login" : "Filter Chart" }}</md-dialog-title>
        </div>

        <div class="utility-dialog-box_login" v-if="dialog.status">
          <div v-if="dialog.share" style="margin-right: .1rem !important">
            <md-field style="max-width: 100%">
              <label>Chart Link</label>
              <md-textarea  id="sharedlinktext" v-model="dialog.chart" md-counter="150">{{ dialog.chart }}</md-textarea>
            </md-field>
            <span class="md-subheading"> {{ dialog.message }}</span>
          </div>
          <div v-else-if="dialog.tableview" style="margin-right: .8rem !important;">
            <div class="viz-intro-query" style="min-height: 40rem !important">
              <yasr v-bind:results="dialog.tableview"></yasr>
            </div>
          </div>
          <div v-else-if="dialog.query" style="margin-right: .8rem !important;">
            <div class="viz-intro-query">
              <yasqe v-model="dialog.query" :showBtns='true'></yasqe>
            </div>
            <span class="md-subheading"> {{ dialog.message }}</span>
          </div>
          <div v-else> <span class="md-subheading">{{ dialog.message }}</span> </div>
          
          <div class="utility-margin-big viz-2-col" v-if="dialog.share || dialog.delete || dialog.query || dialog.diag || dialog.tableview">
            <div class="utility-margin-top"></div>
            <div class="utility-align--right utility-margin-top" v-if="dialog.share || dialog.query || dialog.tableview">
              <a @click.prevent="cancelDel" class="btn-text btn-text--default">Close</a>
            </div>
            <div class="utility-align--right utility-margin-top" v-else-if="dialog.delete || dialog.diag">
              <a @click.prevent="cancelDel" class="btn-text btn-text--default">Close</a> &nbsp; &nbsp;
              <a @click.prevent="dialogAction" class="btn-text btn-text--default" v-if="!dialog.btn">{{dialog.title}}</a>
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