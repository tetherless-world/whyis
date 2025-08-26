<template>
  <!-- Bootstrap Offcanvas for navigation drawer -->
  <div 
    class="offcanvas offcanvas-start" 
    tabindex="-1" 
    id="navigationDrawer"
    :class="{ show: menuVisible }"
    data-mdb-backdrop="false"
  >
    <div class="offcanvas-header">
      <h5 class="offcanvas-title">App Navigation</h5>
      <button 
        type="button" 
        class="btn-close text-reset" 
        @click="menuVisible = false"
        aria-label="Close"
      ></button>
    </div>
    <div class="offcanvas-body p-0">
      <div class="list-group list-group-flush">
        <a 
          href="#" 
          class="list-group-item list-group-item-action"
          @click.prevent="navTo('/')"
        >
          <i class="material-icons me-3">home</i>
          Home
        </a>
        
        <a 
          href="#" 
          class="list-group-item list-group-item-action"
          @click.prevent="navTo('/wi/home')"
        >
          <i class="material-icons me-3">widgets</i>
          Facet Browser
        </a>
        
        <a 
          href="#" 
          class="list-group-item list-group-item-action"
          @click="navTo('/sparql.html')"
        >
          <i class="material-icons me-3">web</i>
          Sparql
          <small class="text-muted d-block">Sparql Browser</small>
        </a>
        
        <a 
          href="#" 
          class="list-group-item list-group-item-action"
          @click="navTo('gallery', 'http://semanticscience.org/resource/Chart')"
        >
          <i class="material-icons me-3">view_comfy</i>
          Browse Visualization
          <small class="text-muted d-block">Visualization Gallery</small>
        </a>
        
        <a 
          v-if="authenticated.email == undefined" 
          href="#" 
          class="list-group-item list-group-item-action"
          @click="navTo(loginNav)"
        >
          <i class="material-icons me-3">fingerprint</i>
          Login
        </a>
      </div>
      
      <!-- User Dashboard Section -->
      <div v-if="authenticated.email !== undefined" class="mt-4">
        <h6 class="px-3 text-muted">User Dashboard</h6>
        <div class="list-group list-group-flush">
          <a 
            href="#" 
            class="list-group-item list-group-item-action"
            @click="navTo('new', 'http://semanticscience.org/resource/Chart')"
          >
            <i class="material-icons me-3">add</i>
            Create New Visualization
          </a>
          
          <a 
            href="#" 
            class="list-group-item list-group-item-action"
            @click.prevent="navDataSet"
          >
            <i class="material-icons me-3">publish</i>
            New Dataset Upload
          </a>
          
          <a 
            v-if="authenticated.admin == 'False'" 
            href="#" 
            class="list-group-item list-group-item-action"
            @click="navTo(logoutNav)"
          >
            <i class="material-icons me-3">arrow_back_ios</i>
            Sign Out
          </a>
        </div>
      </div>
      
      <!-- Administration Dashboard Section -->
      <div v-if="authenticated.admin=='True'" class="mt-4">
        <h6 class="px-3 text-muted">Administration Dashboard</h6>
        <div class="list-group list-group-flush">
          <a 
            href="#" 
            class="list-group-item list-group-item-action"
            @click="navTo('manage', 'http://semanticscience.org/resource/Chart')"
          >
            <i class="material-icons me-3">restore</i>
            Restore Chart
          </a>
          
          <a 
            href="#" 
            class="list-group-item list-group-item-action"
          >
            <i class="material-icons me-3">insights</i>
            Admin Dashboard
          </a>
          
          <a 
            href="#" 
            class="list-group-item list-group-item-action"
            @click="navTo(logoutNav)"
          >
            <i class="material-icons me-3">arrow_back_ios</i>
            Sign Out
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" src="../../assets/css/main.scss"></style>

<script>
import EventServices from '../../modules/events/event-services'

export default {
  name: 'Drawer',
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
}
</script>