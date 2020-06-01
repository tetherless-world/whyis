<template>
  <md-app-drawer :md-active.sync="menuVisible">
    <md-toolbar class="md-transparent" md-elevation="0">
      App Navigation
    </md-toolbar>
    <md-divider></md-divider>
    <md-list class="utility-transparentbg">
      <md-list-item class="utility-navadjust">
        <md-icon class="utility-navfonticon">home</md-icon>
        <span class="md-list-item-text utility-navfont">Facet Browser</span>
      </md-list-item>

      <md-list-item class="utility-navadjust">
        <md-icon class="utility-navfonticon">home_work</md-icon>
        <span class="md-list-item-text utility-navfont">Materialsmine</span>
      </md-list-item>

      <div class="utility-space" v-if="authenticated"></div>

      <md-toolbar class="md-transparent" md-elevation="0" v-if="authenticated">
        User Dashboard
      </md-toolbar>

      <md-divider v-if="authenticated"></md-divider>
      <md-list-item class="utility-nav_bottom-margin" v-if="authenticated">
        <md-switch v-model="booleans" class="md-primary">Switch Theme</md-switch>
      </md-list-item>

      <md-list-item class="utility-navadjust" v-if="authenticated" v-on:click.prevent="myChartNavigation('Create New')">
        <md-icon class="utility-navfonticon">add</md-icon>
        <span class="md-list-item-text utility-navfont">Create New</span>
      </md-list-item>

      <md-list-item class="utility-navadjust" v-if="authenticated" v-on:click.prevent="myChartNavigation('My Chart')">
        <md-icon class="utility-navfonticon">insert_chart_outlined</md-icon>
        <span class="md-list-item-text utility-navfont">My Charts</span>
      </md-list-item>

      <md-list-item class="utility-navadjust" v-if="authenticated" v-on:click.prevent="myChartNavigation('Notification')">
        <md-icon class="utility-navfonticon">notifications_none</md-icon>
        <span class="md-list-item-text utility-navfont">Notification</span>
      </md-list-item>

      <md-list-item class="utility-navadjust" v-if="authenticated" v-on:click.prevent="myChartNavigation('Settings')">
        <md-icon class="utility-navfonticon">settings</md-icon>
        <span class="md-list-item-text utility-navfont">Settings</span>
      </md-list-item>

      <md-list-item class="utility-navadjust" v-if="authenticated" v-on:click.prevent="myChartNavigation('Sign Out')">
        <md-icon class="utility-navfonticon">arrow_back_ios</md-icon>
        <span class="md-list-item-text utility-navfont">Sign Out</span>
      </md-list-item>
    </md-list>
  </md-app-drawer>
</template>

<script>

import { eventCourier as ec } from '../../store';
import { router } from '../../router/routes'
export default {
  name: 'Drawer',
  mixins: [router],
  props:{
    authenticated: {
      type: Boolean
    }
  },
  data() {
    return {
      booleans: false,  //for switching themes
      menuVisible: false
    }
  },
  watch:{
    booleans(value){
      ec.changeTheme(value)
    }
  },
  created() {
    ec.$on('togglenavigation', (data) => {
      return this.menuVisible = data
    });
  },
  methods: {
    myChartNavigation(args){
      if(args == "Sign Out") {
        ec.getAuth()
        return this.changeRoute("home")
      }
      return this.changeRoute("home", args)
    }
  }
}
</script>

<style scoped lang="scss" src="../../static/css/main.scss"></style>