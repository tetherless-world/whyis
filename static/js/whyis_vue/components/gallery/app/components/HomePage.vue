<template>
  <div>
  <div class="page-container">
    <md-app md-waterfall md-mode="overlap">
      <md-app-toolbar :authenticated="authenticated" />
      <md-app-drawer :authenticated="authenticated" :globalargs="globalargs" />
      <md-app-content class="utility-bg utility-bg_border">
        <viz-grid :globalargs="globalargs" :authenticated="authenticated.status" />
      </md-app-content>
    </md-app>
    <md-speed-dial :class="bottomPosition">
      <md-speed-dial-target class="utility-float-icon">
        <md-icon>menu</md-icon>
      </md-speed-dial-target>

      <md-speed-dial-content>
         <md-button class="md-icon-button">
          <md-tooltip class="utility-bckg" md-direction="left"> Cancel Filter </md-tooltip>
          <md-icon class="utility-color">search_off</md-icon>
        </md-button>
        <md-button class="md-icon-button" @click="showFilterBox">
          <md-tooltip class="utility-bckg" md-direction="left"> Filter </md-tooltip>
          <md-icon class="utility-color">search</md-icon>
        </md-button>
         <md-button class="md-icon-button" v-if="authenticated.status" @click.prevent="newChart">
          <md-tooltip class="utility-bckg" md-direction="left">Create New Chart</md-tooltip>
          <md-icon class="utility-color">add</md-icon>
        </md-button>
      </md-speed-dial-content>
    </md-speed-dial>
  </div>
  <FilterBox />
  </div>
</template>
<style scoped lang="scss" src="../static/css/main.scss"></style>
<script>
  import { eventCourier as ec } from '../store'
  import { router } from '../router/routes'
  import Header from './header/Header'
  import Drawer from './header/Drawer'
  import FilterBox from './Filter'
  import vizGrid from './Vizgrid'
  import { goToView } from '../../../../utilities/views'
  export default {
    name: 'homePage',
    mixins: [router],
    props:{
      globalargs: {
        type: String,
        require: true,
        default: () => {
          return "http://semanticscience.org/resource/Chart"
        }
      }
    },
    data() {
      return {
        filter: false,
        bottomPosition:'md-bottom-right',
        authenticated: ec.authenticated,
        pageArgs: null,
      }
    },
    components: {
      FilterBox,
      vizGrid,
      mdAppToolbar: Header,
      mdAppDrawer: Drawer,
    },
    methods: {
      showFilterBox () {
        ec.$emit('open-filter-box', {open: true, type: "filter"});
        return this.filter = true
      },
      newChart(){
        ec.$emit('togglenavigation', false);
        return goToView(this.globalargs, "new", "open")
      }
    },
    created() {
      // SearchBox Listener!!!
      ec
      .$on('close-filter-box', (data) => this.filter = data)
      .$on('isauthenticated', (data) => this.authenticated = data)
      .$on("route-args", (data) => this.pageArgs = data)
      ec.getAuth()
    }
  }
</script>