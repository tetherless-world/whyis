<template>
  <div style="position: relative">
    <div class="viz-dark-loading" v-if="loading">
      <spinner :loading="loading" />
    </div>
    <div class="viz-setting">
      <div class="viz-setting-links">
        <md-list>
          <md-list-item id="restore" class="utility-gridborder" v-on:click.prevent="actionManager('restore')">
            <md-icon class="utility-navfonticon">sync</md-icon>
            <span id="css-adjust-navfont" class="md-list-item-text utility-navfont">Restore From Backup</span>
          </md-list-item>
        </md-list>
        <md-list>
          <md-list-item id="enable" v-on:click.prevent="actionManager('enable')">
            <md-icon class="utility-navfonticon">visibility</md-icon>
            <span id="css-adjust-navfont" class="md-list-item-text utility-navfont">Enable Charts</span>
          </md-list-item>
        </md-list>
        <md-list>
          <md-list-item id="disable" v-on:click.prevent="actionManager('disable')">
            <md-icon class="utility-navfonticon">visibility_off</md-icon>
            <span id="css-adjust-navfont" class="md-list-item-text utility-navfont">Hide Charts</span>
          </md-list-item>
        </md-list>
        <md-list>
          <md-list-item v-on:click.prevent="navBack">
            <md-icon class="utility-navfonticon">domain</md-icon>
            <span id="css-adjust-navfont" class="md-list-item-text utility-navfont">Return Home</span>
          </md-list-item>
        </md-list>
      </div>
      <div class="viz-setting-content">
        <div class="utility-gridicon-single" style="padding-right: 2rem">
          <div>
            <md-button class="md-icon-button" @click.native.prevent="navBack">
              <md-tooltip class="utility-bckg" md-direction="bottom"> Go Back </md-tooltip>
              <md-icon>arrow_back</md-icon>
            </md-button>
          </div>
          <div v-if="actionType == 'restore'">
            <md-button class="md-icon-button" @click.native.prevent="restoreAllChart"> 
              <md-tooltip class="utility-bckg" md-direction="top"> Reset All </md-tooltip>
              <md-icon>cached</md-icon>
            </md-button>
          </div>
          <div v-else-if="actionType == 'disable'">
            <md-button class="md-icon-button" @click.native.prevent="chartQuery"> 
              <md-tooltip class="utility-bckg" md-direction="bottom"> Disable All Charts </md-tooltip>
              <md-icon>visibility_off</md-icon>
            </md-button>
          </div>
          <div v-else-if="actionType == 'enable'">
            <md-button class="md-icon-button" @click.native.prevent="chartQuery"> 
              <md-tooltip class="utility-bckg" md-direction="bottom"> Enable All Charts </md-tooltip>
              <md-icon>visibility</md-icon>
            </md-button>
          </div>
        </div>
        <div v-if="!userManage && !createTag">
          <md-table v-model="searched" md-sort="name" md-sort-order="asc" style="margin-top: 3rem">
            <md-table-toolbar style="margin-bottom: 1.8rem">
              <div class="md-toolbar-section-start">
                <h1 class="md-title">Charts List</h1>
              </div>

              <md-field md-clearable class="md-toolbar-section-end">
                <md-input placeholder="Search By Chart Title..." v-model="search" @input="searchOnTable" />
              </md-field>
            </md-table-toolbar>

            <md-table-empty-state
              md-label="No Chart Found"
              :md-description="`No chart found for this '${search}' query. Try a different search title or create a new chart.`">
              <md-button class="md-primary md-raised" @click="newChart">Create New Chart</md-button>
            </md-table-empty-state>
            
            <md-table-row slot="md-table-row" slot-scope="{ item }">
              <md-table-cell md-label="Nano Pub ID">{{ item.name.toUpperCase() }}</md-table-cell>
              <md-table-cell md-label="Title" md-sort-by="backup.title">{{ item.backup.title }}</md-table-cell>
              <md-table-cell md-label="Description" md-sort-by="backup.description">{{ reduceDescription(item.backup.description) }}</md-table-cell>
              <md-table-cell md-label="Restore" v-if="actionType == 'restore'">
                <md-button class="md-icon-button" @click.prevent="restoreChartsBk(item)">
                  <md-tooltip class="utility-bckg" md-direction="left"> Restore </md-tooltip>
                  <md-icon class="utility-color">cached</md-icon>
                </md-button>
            </md-table-cell>
            <md-table-cell md-label="Disable" v-else-if="actionType == 'disable'">
                <md-button class="md-icon-button" @click.prevent="disableChart(item)">
                  <md-tooltip class="utility-bckg" md-direction="left"> Disable </md-tooltip>
                  <md-icon class="utility-color">visibility_off</md-icon>
                </md-button>
            </md-table-cell>
            <md-table-cell md-label="Enable" v-else-if="actionType == 'enable'">
                <md-button class="md-icon-button" @click.prevent="enableChart(item)">
                  <md-tooltip class="utility-bckg" md-direction="left"> Enable </md-tooltip>
                  <md-icon class="utility-color">visibility</md-icon>
                </md-button>
            </md-table-cell>
            </md-table-row>
          </md-table>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
  .md-autocomplete {

  }
</style>
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import { EventServices, Slug } from '../../../../modules'
  import { saveChart, getDefaultChart, } from '../../../../utilities/vega-chart'
  import { goToView } from '../../../../utilities/views'

  String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
  };

  export default Vue.component('vega-restore', {
    data() {
      return {
        loading: false,
        actionType: 'restore',
        results: [],
        newResults: [],
        search: null,
        searched: [],
        authenticated: EventServices.authUser,
        userManage: false,
        createTag: false,
        tagTitle: null,
        tagDesc: null,
        tagURI: null,
        tagError: false,
      }
    },
    computed: {
      messageClass () {
        return {
          'md-invalid': this.tagError
        }
      }
    },
    watch:{
      actionType(nv, ov){
        const makeInactive = document.getElementById(ov);
        if(makeInactive){
          makeInactive.classList.remove('utility-gridborder')
        }
      },
    },
    methods: {
      navBack(){
        return EventServices.navTo('view', 'http://semanticscience.org/resource/Chart')
      },
      restoreAllChart(){
        return EventServices.$emit("dialoguebox", {status: true, diag:true, reset: true, title: "Reset Chart DB", message: `Are you sure you want to reset the chart database?`})
      },
      searchOnTable () {
        this.searched = this.searchByName(this.newResults, this.search)
      },
      searchByName(items, term){
        if(term) {
          return items.filter(item => this.toLower(item.backup.title).includes(this.toLower(term)))
        }
        return items
      },
      toLower(text) {
        return text.toString().toLowerCase()
      },
      reduceDescription(args) {
        let arr, arrSplice
        arr = args.split(" ")
        if(arr.length > 16){
          arr.splice(15)
          arrSplice = arr.reduce((a,b) => `${a} ${b}`, "")
          return `${arrSplice}...`;
        } else {
          return args;
        }
      },
      async actionManager(arg){
        this.actionType = !arg ? 'restore': arg;
        this.userManage = false;
        this.createTag = false;
        const element = document.getElementById(this.actionType)
        if(element) element.classList.add('utility-gridborder')

        if(this.actionType == 'userManage'){
          this.userManage = true;
          const userResult = await EventServices.getUserList()
          this.searched = userResult.users;
        } else if(this.actionType == 'restore'){
          this.newResults = await this.results.filter((el) => el.restored == false)
          this.searched = this.results.filter((el) => el.restored == false)
        } else if(this.actionType == 'enable'){
          this.newResults = await this.results.filter((el) => el.enabled == false)
          this.searched = this.results.filter((el) => el.enabled == false) 
        } else if(this.actionType == 'disable'){
          this.newResults = await this.results.filter((el) => el.enabled == true)
          this.searched = this.results.filter((el) => el.enabled == true)
        } else if(this.actionType == 'createtags') {
          this.createTag = true;
        } else {
          return
        }
      },
      newChart(){
        EventServices.$emit('togglenavigation', false);
        return EventServices.navTo("new", true)
      },
      restoreChartsBk(args){
        if (typeof(Storage) !== "undefined") {
          sessionStorage.setItem("chart", JSON.stringify(args));
          return EventServices.navTo("restore", 'http://semanticscience.org/resource/Chart')
        }
        EventServices.$emit('snacks', {status:true, message: 'No Browser Support!!!'});
      },
      async disableChart(args){
        this.loading = true;
        const res = await EventServices.createBackUp(args.backup, 'null', false);
        if(res.mssg){
          this.results.filter(el => {
            if(el.name == args.name){
              el.enabled = false
            }
          })
          this.actionManager('disable')
          EventServices.$emit('snacks', {status:true, message: 'Chart Disabled Successfully'});
          this.loading = false;
        } else {
          EventServices.$emit('snacks', {status:true, message: 'Error disabling chart'});
          this.loading = false;
        }
      },
      async enableChart(args){
        this.loading = true;
        const res = await EventServices.createBackUp(args.backup, null, true);
        if(res.mssg){
          this.results.filter(el => {
            if(el.name == args.name){
              el.enabled = true
            }
          })
          this.actionManager('enable')
          EventServices.$emit('snacks', {status:true, message: 'Chart Enabled Successfully'});
          this.loading = false;
        } else {
          EventServices.$emit('snacks', {status:true, message: 'Error enabling chart'});
          this.loading = false;
        }
      },
      async filterResults(){
        if(!this.results.length){
          return;
        } else {
          this.newResults = await this.results.filter((el) => el.restored == false)
          this.searched = this.newResults;
          this.actionOpt = {btn:'Restore All'}
        }
      }
    },
    beforeMount(){
      return this.filterResults()
    },
    created () {
      EventServices
      .$on("appstate", (data) => this.results = data)
      .$on('isauthenticated', (data) => this.authenticated = data)
      .$on("reloadrestored", (data) => {
        this.results = EventServices.chartListings;
        this.filterResults()
      })
      this.results = EventServices.chartListings;
    }
  })
</script>