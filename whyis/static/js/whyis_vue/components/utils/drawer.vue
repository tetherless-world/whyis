<template>
  <div class="offcanvas offcanvas-start" tabindex="-1" :class="{'show': menuVisible}" data-bs-backdrop="false">
    <div class="offcanvas-header">
      <h5 class="offcanvas-title">App Navigation</h5>
      <button type="button" class="btn-close text-reset" @click="menuVisible = false" aria-label="Close"></button>
    </div>
    <hr>
    <div class="offcanvas-body utility-transparentbg">
      <div class="list-group list-group-flush">
        <div class="nav-item-wrapper">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click.prevent="navTo('/')">
            <i class="bi bi-house-fill utility-navfonticon me-3"></i>
            <span class="utility-navfont">Home</span>
          </a>
        </div>
        <div class="nav-item-wrapper">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click.prevent="navTo('/wi/home')">
            <i class="bi bi-grid-3x3-gap-fill utility-navfonticon me-3"></i>
            <span class="utility-navfont">Facet Browser</span>
          </a>
        </div>
        <div class="nav-item-wrapper">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo('/sparql.html')" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Sparql Browser">
            <i class="bi bi-globe utility-navfonticon me-3"></i>
            <span class="utility-navfont">Sparql</span>
          </a>
        </div>
        <div class="nav-item-wrapper">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo('gallery', 'http://semanticscience.org/resource/Chart')" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Visualization Gallery">
            <i class="bi bi-grid utility-navfonticon me-3"></i>
            <span class="utility-navfont">Browse Visualization</span>
          </a>
        </div>
        <div class="nav-item-wrapper" v-if="authenticated.email == undefined">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo(loginNav)">
            <i class="bi bi-fingerprint utility-navfonticon me-3"></i>
            <span class="utility-navfont">Login</span>
          </a>
        </div>

        <div class="utility-space" v-if="authenticated.email"></div>

        <div v-if="authenticated.email !== undefined" class="mt-4">
          <h6 class="text-muted ps-3">User Dashboard</h6>
          <hr>
        </div>

        <div class="nav-item-wrapper" v-if="authenticated.email !== undefined">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo('new', 'http://semanticscience.org/resource/Chart')">
            <i class="bi bi-plus-circle utility-navfonticon me-3"></i>
            <span class="utility-navfont">Create New Visualization</span>
          </a>
        </div>
        <div class="nav-item-wrapper" v-if="authenticated.email !== undefined">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click.prevent="navDataSet">
            <i class="bi bi-upload utility-navfonticon me-3"></i>
            <span class="utility-navfont">New Dataset Upload</span>
          </a>
        </div>

        <div class="nav-item-wrapper" v-if="authenticated.admin == 'False'">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo(logoutNav)">
            <i class="bi bi-arrow-left utility-navfonticon me-3"></i>
            <span class="utility-navfont">Sign Out</span>
          </a>
        </div>
        
        <div class="utility-space" v-if="authenticated.admin=='True'"></div>

        <div v-if="authenticated.admin=='True'" class="mt-4">
          <h6 class="text-muted ps-3">Administration Dashboard</h6>
          <hr>
        </div>

        <div class="nav-item-wrapper" v-if="authenticated.admin == 'True'">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo('manage', 'http://semanticscience.org/resource/Chart')">
            <i class="bi bi-arrow-clockwise utility-navfonticon me-3"></i>
            <span class="utility-navfont">Restore Chart</span>
          </a>
        </div>
        <div class="nav-item-wrapper" v-if="authenticated.admin == 'True'">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center">
            <i class="bi bi-speedometer2 utility-navfonticon me-3"></i>
            <span class="utility-navfont">Admin Dashboard</span>
          </a>
        </div>
        <div class="nav-item-wrapper" v-if="authenticated.admin == 'True'">
          <a href="#" class="list-group-item list-group-item-action utility-navadjust d-flex align-items-center" @click="navTo(logoutNav)">
            <i class="bi bi-arrow-left utility-navfonticon me-3"></i>
            <span class="utility-navfont">Sign Out</span>
          </a>
        </div>
      </div>
    </div>
  </div>
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