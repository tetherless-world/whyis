<template>
  <div>
    <md-app-toolbar class="md-primary md-large nav-bg">
        <div class="md-toolbar-row">
          <md-button class="md-icon-button" @click="toggle">
            <md-icon>menu</md-icon>
          </md-button>
          <span class="md-title nav-title" v-if="otherArgs != null && authenticated.status">Visualization Gallery - {{ otherArgs }}</span>
          <span class="md-title nav-title" v-else>Visualization Gallery</span>
          <div class="md-toolbar-section-end">
            <md-button class="md-icon-button" v-if="authenticated.status">
              <md-avatar>
                <img src="/static/js/whyis_vue/components/gallery/app/static/image/default.jpg" alt="Avatar">
              </md-avatar>
            </md-button>
            <span class="md-subheading utility-cursor" v-else @click="login">Login</span>
            
          </div>
        </div>
    </md-app-toolbar>
    <md-snackbar :md-position="position" :md-duration="isInfinity ? Infinity : duration" :md-active.sync="showSnackbar" md-persistent>
      <span>You are now logged in!</span>
      <md-button class="md-primary" @click="showSnackbar = false">OK, Let's Explore</md-button>
    </md-snackbar>
  </div>
</template>

<style scoped lang="scss" src="../../static/css/main.scss"></style>

<script>
import { eventCourier as ec } from '../../store';
export default {
  name: 'Header',
  props:{
    authenticated: {
      type: Object
    }
  },
  data(){
    return {
      profileImage: null,
      otherArgs: null,
      showSnackbar: false,
      position: 'center',
      duration: 4000,
      isInfinity: false
    }
  },
  methods:{
    toggle(){
      return ec.toggleNav()
    },
    login(){
      return window.location = window.location.origin + "/login"
      // ec.$emit('open-filter-box', {open: true, type: "login"});
    }
  },
  created(){
    ec
    .$on("route-args", (data) => this.otherArgs = data)
    .$on('isauthenticated', (data) => this.showSnackbar = data.status);
  }
}
</script>