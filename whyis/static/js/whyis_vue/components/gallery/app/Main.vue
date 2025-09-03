<template>
  <div>
    <div v-if="loading">
      <spinner :loading="loading" :text='loadingText'/>
    </div>
    <div v-else>
      <viz-grid :authenticated="authenticated" :instancetype="instancetype"/>
      <!-- Bootstrap Speed Dial Replacement -->
      <div class="position-fixed bottom-0 end-0 p-3">
        <div class="dropdown dropup">
          <button class="btn btn-primary rounded-circle p-3 utility-float-icon" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="width: 56px; height: 56px;">
            <i class="bi bi-list"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" @click="cancelFilter">
                <i class="bi bi-search-heart utility-color me-2"></i>
                <span>Cancel Filter</span>
              </a>
            </li>
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" @click="showFilterBox">
                <i class="bi bi-search utility-color me-2"></i>
                <span>Filter</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import EventServices from '../../../modules/events/event-services'
  import vizGrid from './components/Vizgrid.vue'
  export default Vue.component('viz-gallery', {
    props:{
      instancetype: {
        type: String,
        require: true
      }
    },
    data() {
      return {
        filter: false,
        bottomPosition:'bottom-0 end-0',
        speedDials: EventServices.speedDials,
        authenticated: EventServices.authUser,
        charts:[],
        loading: false,
        loadingText: "loading up..."
      }
    },
    components: {
      vizGrid,
    },
    methods: {
      showFilterBox () {
        // EventServices.$emit('open-filter-box', {open: true, type: "filter"});
        // return this.filter = true
      },
      cancelFilter(){
        // return EventServices.cancelChartFilter();
      }
    },
    created() {
      EventServices
      .$on('close-filter-box', (data) => this.filter = data)
      .$on('isauthenticated', (data) => this.authenticated = data)
    }
  })
</script>
