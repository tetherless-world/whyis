<template>
  <div style="position: relative">
    <div class="viz-dark-loading" v-if="loading">
      <spinner :loading="loading" />
    </div>
    <div class="viz-setting">
      <div class="viz-setting-links">
        <ul class="list-group">
          <li class="list-group-item utility-gridborder d-flex align-items-center" id="restore" v-on:click.prevent="actionManager('restore')">
            <i class="bi bi-arrow-clockwise utility-navfonticon me-2"></i>
            <span id="css-adjust-navfont" class="utility-navfont">Restore From Backup</span>
          </li>
        </ul>
        <ul class="list-group">
          <li class="list-group-item d-flex align-items-center" id="enable" v-on:click.prevent="actionManager('enable')">
            <i class="bi bi-eye utility-navfonticon me-2"></i>
            <span id="css-adjust-navfont" class="utility-navfont">Enable Charts</span>
          </li>
        </ul>
        <ul class="list-group">
          <li class="list-group-item d-flex align-items-center" id="disable" v-on:click.prevent="actionManager('disable')">
            <i class="bi bi-eye-slash utility-navfonticon me-2"></i>
            <span id="css-adjust-navfont" class="utility-navfont">Hide Charts</span>
          </li>
        </ul>
        <ul class="list-group">
          <li class="list-group-item d-flex align-items-center" v-on:click.prevent="navBack">
            <i class="bi bi-house utility-navfonticon me-2"></i>
            <span id="css-adjust-navfont" class="utility-navfont">Return Home</span>
          </li>
        </ul>
      </div>
      <div class="viz-setting-content">
        <div class="utility-gridicon-single d-flex gap-2" style="padding-right: 2rem">
          <div>
            <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="navBack">
              <i class="bi bi-arrow-left"></i>
              <span class="visually-hidden">Go Back</span>
            </button>
          </div>
          <div v-if="actionType == 'restore'">
            <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="restoreAllChart">
              <i class="bi bi-arrow-clockwise"></i>
              <span class="visually-hidden">Reset All</span>
            </button>
          </div>
          <div v-else-if="actionType == 'disable'">
            <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="chartQuery">
              <i class="bi bi-eye-slash"></i>
              <span class="visually-hidden">Disable All Charts</span>
            </button>
          </div>
          <div v-else-if="actionType == 'enable'">
            <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="chartQuery">
              <i class="bi bi-eye"></i>
              <span class="visually-hidden">Enable All Charts</span>
            </button>
          </div>
        </div>
        <div v-if="!userManage && !createTag">
          <div class="table-responsive" style="margin-top: 3rem">
            <!-- Bootstrap table header -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h1 class="h4">Charts List</h1>
              <div class="input-group" style="width: 300px;">
                <input type="search" class="form-control" placeholder="Search By Chart Title..." v-model="search" @input="searchOnTable">
                <button class="btn btn-outline-secondary" type="button" @click="search = ''">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>

            <div v-if="searched.length === 0" class="text-center py-5">
              <div class="mb-3">
                <h5>No Chart Found</h5>
                <p class="text-muted">No chart found for this '{{search}}' query. Try a different search title or create a new chart.</p>
              </div>
              <button type="button" class="btn btn-primary" @click="newChart">Create New Chart</button>
            </div>
            
            <table v-else class="table table-striped">
              <thead>
                <tr>
                  <th scope="col">Nano Pub ID</th>
                  <th scope="col">Title</th>
                  <th scope="col">Description</th>
                  <th scope="col" v-if="actionType == 'restore'">Restore</th>
                  <th scope="col" v-else-if="actionType == 'disable'">Disable</th>
                  <th scope="col" v-else-if="actionType == 'enable'">Enable</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in searched" :key="item.name">
                  <td>{{ item.name.toUpperCase() }}</td>
                  <td>{{ item.backup.title }}</td>
                  <td>{{ reduceDescription(item.backup.description) }}</td>
                  <td v-if="actionType == 'restore'">
                    <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="restoreChartsBk(item)">
                      <i class="bi bi-arrow-clockwise utility-color"></i>
                      <span class="visually-hidden">Restore</span>
                    </button>
                  </td>
                  <td v-else-if="actionType == 'disable'">
                    <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="disableChart(item)">
                      <i class="bi bi-eye-slash utility-color"></i>
                      <span class="visually-hidden">Disable</span>
                    </button>
                  </td>
                  <td v-else-if="actionType == 'enable'">
                    <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="enableChart(item)">
                      <i class="bi bi-eye utility-color"></i>
                      <span class="visually-hidden">Enable</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
  .autocomplete {
    /* Bootstrap autocomplete styles */
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
          'is-invalid': this.tagError
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