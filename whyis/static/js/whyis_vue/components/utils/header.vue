<template>
  <div>
    <md-app-toolbar class="md-primary md-large nav-bg">
        <div class="md-toolbar-row">
          <md-button class="md-icon-button" @click="toggle">
            <md-icon>menu</md-icon>
          </md-button>
          <span class="md-title nav-title viz-u-mgup-md"> {{ site_name }} <span class="md-body-1 viz-u-display__show">{{ page_title }}</span></span>
          <div class="md-toolbar-section-end">
            <div class="nav-header-intro" v-if="authenticated !== undefined">
              <span class="md-subheading" style="display:inline-block; padding-top:.5rem">Learn</span>
              <md-button class="md-icon-button" style="margin-left: -.5rem !important;" href="http://tetherless-world.github.io/whyis/" target="_blank">
                <md-icon>info</md-icon>
              </md-button>
            </div>
            <div v-if="authenticated !== undefined" class="viz-u-display__desktop">
              <div style="display:inline-block; padding-top:.5rem"><span class="md-subheading">{{ authenticated.name }}</span></div>
              <md-button class="md-icon-button">
                <md-avatar>
                  <img src="/images/default.jpg" alt="Avatar">
                </md-avatar>
              </md-button>
            </div>
            <a class="md-subheading utility-cursor btn-text btn-text--white utility-margin-right" v-if="authenticated == undefined" :href="registerNav">Sign up</a>
            <a class="md-subheading utility-cursor btn-text btn-text--white" v-if="authenticated == undefined" :href="loginNav">Login</a>
          </div>
        </div>
    </md-app-toolbar>
    <md-snackbar :md-position="position" :md-duration="isInfinity ? Infinity : duration" :md-active.sync="showSnackbar" md-persistent>
      <span v-if="snackMssg == null">You are now logged in!</span>
      <span v-else>{{ snackMssg }}</span>
      <md-button class="md-primary" @click="showSnackbar = false" v-if="snackTip == null">OK, Let's Explore</md-button>
      <md-button class="md-primary" @click="showSnackbar = false" v-else>{{ snackTip }}</md-button>
    </md-snackbar>
  </div>
</template>

<style lang="scss" src="../../assets/css/main.scss"></style>

<script>
import Vue from 'vue';
import EventServices from '../../modules/events/event-services';
export default Vue.component('Header', {
  props: ['site_name', 'page_title', 'registerNav', 'loginNav'],
  data(){
    return {
      profileImage: null,
      otherArgs: null,
      showSnackbar: false,
      snackMssg: null,
      snackTip: null,
      position: 'center',
      duration: 4000,
      isInfinity: false,
      authenticated: EventServices.authUser
    }
  },
  watch: {
    showSnackbar(newValue, oldValue){
        if(newValue == true){
            setTimeout(()=>{
                this.showSnackbar = false
            }, this.duration)
        } else if(newValue == false){
            this.snackMssg = null;
            this.snackTip = null;
        }
    }
  },
  methods:{
    toggle(){
        return EventServices.toggleNav()
    },
    confirmAuths(){
        if(!EventServices.authUser){
            return EventServices.confirmAuth()
        }
    }
  },
  created(){
    EventServices
    .$on("snacks", data => {
        this.showSnackbar = data.status;
        this.snackMssg = data.message;
        this.snackTip = data.tip
    })
    .$on('isauthenticated', data => this.authenticated = data)
  }
})
</script>