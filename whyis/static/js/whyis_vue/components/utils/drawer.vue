<template>
  <md-app-drawer :md-active.sync="menuVisible">
    <md-toolbar class="md-transparent" md-elevation="0">
      App Navigation
    </md-toolbar>
    <md-divider></md-divider>
    <md-list class="utility-transparentbg">
      <div class="md-drawer-div">
        <md-list-item class="utility-navadjust" @click.prevent="navTo('/')">
          <md-icon class="utility-navfonticon">home</md-icon>
          <span class="md-list-item-text utility-navfont">Home</span>
        </md-list-item>
      </div>
      <div class="md-drawer-div">
        <md-list-item class="utility-navadjust" @click.prevent="navTo('/wi/home')">
          <md-icon class="utility-navfonticon">widgets</md-icon>
          <span class="md-list-item-text utility-navfont">Facet Browser</span>
        </md-list-item>
      </div>
      <div class="md-drawer-div">
        <md-list-item class="utility-navadjust" @click="navTo('/sparql.html')">
          <md-icon class="utility-navfonticon">web</md-icon>
          <span class="md-list-item-text utility-navfont">Sparql</span>
          <md-tooltip md-direction="bottom">Sparql Browser</md-tooltip>
        </md-list-item>
      </div>
      <div class="md-drawer-div">
        <md-list-item class="utility-navadjust" @click="navTo('gallery', 'http://semanticscience.org/resource/Chart')">
          <md-icon class="utility-navfonticon">view_comfy</md-icon>
          <span class="md-list-item-text utility-navfont">Browse Visualization</span>
          <md-tooltip md-direction="bottom">Visualization Gallery</md-tooltip>
        </md-list-item>
      </div>
      <div class="md-drawer-div" v-if="authenticated.email == undefined">
        <md-list-item class="utility-navadjust" @click="navTo(loginNav)">
          <md-icon class="utility-navfonticon">fingerprint</md-icon>
          <span class="md-list-item-text utility-navfont">Login</span>
        </md-list-item>
      </div>

      <div class="utility-space" v-if="authenticated.email"></div>

      <md-toolbar class="md-transparent" md-elevation="0" v-if="authenticated.email !== undefined">
        User Dashboard
      </md-toolbar>

      <md-divider v-if="authenticated.email !== undefined"></md-divider>
      <div class="md-drawer-div" v-if="authenticated.email !== undefined">
        <md-list-item class="utility-navadjust"  @click="navTo('new', 'http://semanticscience.org/resource/Chart')">
          <md-icon class="utility-navfonticon">add</md-icon>
          <span class="md-list-item-text utility-navfont">Create New Visualization</span>
        </md-list-item>
      </div>
      <div class="md-drawer-div" v-if="authenticated.email !== undefined">
        <md-list-item class="utility-navadjust"  @click.prevent="navDataSet">
          <md-icon class="utility-navfonticon">publish</md-icon>
          <span class="md-list-item-text utility-navfont">New Dataset Upload</span>
        </md-list-item>
      </div>

      <div class="md-drawer-div" v-if="authenticated.admin == 'False'">
        <md-list-item class="utility-navadjust" @click="navTo(logoutNav)">
          <md-icon class="utility-navfonticon">arrow_back_ios</md-icon>
          <span class="md-list-item-text utility-navfont">Sign Out</span>
        </md-list-item>
      </div>
      <div class="utility-space" v-if="authenticated.admin=='True'"></div>

      <md-toolbar class="md-transparent" md-elevation="0" v-if="authenticated.admin=='True'">
        Administration Dashboard
      </md-toolbar>

      <md-divider v-if="authenticated.admin"></md-divider>
       <div class="md-drawer-div" v-if="authenticated.admin == 'True'">
        <md-list-item class="utility-navadjust" @click="navTo('manage', 'http://semanticscience.org/resource/Chart')">
          <md-icon class="utility-navfonticon">restore</md-icon>
          <span class="md-list-item-text utility-navfont">Restore Chart</span>
        </md-list-item>
      </div>
      <div class="md-drawer-div" v-if="authenticated.admin == 'True'">
        <md-list-item class="utility-navadjust">
          <md-icon class="utility-navfonticon">insights</md-icon>
          <span class="md-list-item-text utility-navfont">Admin Dashboard</span>
        </md-list-item>
      </div>
      <div class="md-drawer-div" v-if="authenticated.admin == 'True'">
        <md-list-item class="utility-navadjust" @click="navTo(logoutNav)">
          <md-icon class="utility-navfonticon">arrow_back_ios</md-icon>
          <span class="md-list-item-text utility-navfont">Sign Out</span>
        </md-list-item>
      </div>
    </md-list>
  </md-app-drawer>
</template>

<style lang="scss" src="../../assets/css/main.scss"></style>

<script>
import Vue from 'vue'
import EventServices from '../../modules/events/event-services'
export default Vue.component('Drawer', {
  props: ['logoutNav','loginNav'],
  data() {
    return {
      booleans: false,  //for switching themes
      menuVisible: false,
      resourceType: null,
      myChartEnabled: false,
      myBookmarkEnabled: false,
      authenticated: {
        admin: undefined,
        email: undefined
      }
    }
  },
  methods:{
    navTo(args, uri){
      EventServices.navTo(args, uri)
      return EventServices.$emit('togglenavigation', false)
    },
    navDataSet(){
        EventServices.$emit('togglenavigation', false)
        return window.location = `${window.location.origin}/about?view=new&uri=http:%2F%2Fwww.w3.org%2Fns%2Fdcat%23Dataset`;
    }
  },
  created() {
    EventServices
    .$on('isauthenticated', (data) => {
      if(data.email && data.uri){
        this.authenticated = data
      } 
    })
    .$on('togglenavigation', data => this.menuVisible = data);
  }
})
</script>