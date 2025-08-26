<template>
  <div>
    <!-- Bootstrap Navbar with Material Design styling -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <button 
          class="btn btn-outline-light me-3" 
          type="button" 
          @click="toggle"
          data-mdb-toggle="offcanvas"
          data-mdb-target="#navigationDrawer"
        >
          <i class="material-icons">menu</i>
        </button>
        
        <span class="navbar-brand mb-0 h1">
          {{ site_name }} 
          <span class="fs-6 text-light">{{ page_title }}</span>
        </span>
        
        <div class="d-flex align-items-center">
          <div v-if="authenticated !== undefined" class="me-3">
            <span class="text-light me-2">Learn</span>
            <a 
              class="btn btn-outline-light btn-sm" 
              href="http://tetherless-world.github.io/whyis/" 
              target="_blank"
            >
              <i class="material-icons">info</i>
            </a>
          </div>
          
          <div v-if="authenticated !== undefined" class="d-none d-md-flex align-items-center">
            <span class="text-light me-2">{{ authenticated.name }}</span>
            <button class="btn btn-link p-0">
              <img 
                src="/images/default.jpg" 
                alt="Avatar" 
                class="rounded-circle"
                width="32"
                height="32"
              >
            </button>
          </div>
          
          <a 
            class="btn btn-outline-light me-2" 
            v-if="authenticated == undefined" 
            :href="registerNav"
          >
            Sign up
          </a>
          <a 
            class="btn btn-light" 
            v-if="authenticated == undefined" 
            :href="loginNav"
          >
            Login
          </a>
        </div>
      </div>
    </nav>
    
    <!-- Bootstrap Toast for notifications -->
    <div 
      class="toast-container position-fixed top-0 end-0 p-3"
      style="z-index: 11"
    >
      <div 
        id="loginToast"
        class="toast"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        :class="{ show: showSnackbar }"
        :data-mdb-autohide="!isInfinity"
        :data-mdb-delay="duration"
      >
        <div class="toast-header">
          <strong class="me-auto">Notification</strong>
          <button 
            type="button" 
            class="btn-close" 
            @click="showSnackbar = false"
            aria-label="Close"
          ></button>
        </div>
        <div class="toast-body">
          <span v-if="snackMssg == null">You are now logged in!</span>
          <span v-else>{{ snackMssg }}</span>
          <div class="mt-2 pt-2 border-top">
            <button 
              type="button" 
              class="btn btn-primary btn-sm" 
              @click="showSnackbar = false"
            >
              <span v-if="snackTip == null">OK, Let's Explore</span>
              <span v-else>{{ snackTip }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" src="../../assets/css/main.scss"></style>

<script>
import EventServices from '../../modules/events/event-services';

export default {
  name: 'Header',
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
}
</script>