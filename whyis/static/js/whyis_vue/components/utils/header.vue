<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark nav-bg">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" @click="toggle" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <span class="navbar-brand nav-title viz-u-mgup-md"> 
          {{ site_name }} 
          <span class="navbar-text viz-u-display__show">{{ page_title }}</span>
        </span>
        <div class="d-flex align-items-center">
          <div class="nav-header-intro me-3" v-if="authenticated !== undefined">
            <span class="navbar-text">Learn</span>
            <a class="btn btn-link text-white p-1" href="http://tetherless-world.github.io/whyis/" target="_blank" aria-label="Info">
              <i class="bi bi-info-circle"></i>
            </a>
          </div>
          <div v-if="authenticated !== undefined" class="viz-u-display__desktop d-flex align-items-center">
            <span class="navbar-text me-2">{{ authenticated.name }}</span>
            <div class="dropdown">
              <img src="/images/default.jpg" alt="Avatar" class="rounded-circle" style="width: 32px; height: 32px;">
            </div>
          </div>
          <a class="btn btn-outline-light me-2" v-if="authenticated == undefined" :href="registerNav">Sign up</a>
          <a class="btn btn-outline-light" v-if="authenticated == undefined" :href="loginNav">Login</a>
        </div>
      </div>
    </nav>
    
    <!-- Bootstrap Toast for Snackbar replacement -->
    <div class="toast-container position-fixed top-50 start-50 translate-middle">
      <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" ref="toast" :class="{'show': showSnackbar}">
        <div class="toast-body">
          <span v-if="snackMssg == null">You are now logged in!</span>
          <span v-else>{{ snackMssg }}</span>
          <div class="mt-2 pt-2 border-top">
            <button type="button" class="btn btn-primary btn-sm" @click="showSnackbar = false" v-if="snackTip == null">
              OK, Let's Explore
            </button>
            <button type="button" class="btn btn-primary btn-sm" @click="showSnackbar = false" v-else>
              {{ snackTip }}
            </button>
          </div>
        </div>
      </div>
    </div>
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