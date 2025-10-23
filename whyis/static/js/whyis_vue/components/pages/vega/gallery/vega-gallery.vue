<template>
  <div>
    <div v-if="existingBkmk.status">
      <spinner :loading="existingBkmk.status" :text='existingBkmk.text'/>
    </div>
    <div v-else>
      <viz-grid :authenticated="authenticated" :instancetype="'http://semanticscience.org/resource/Chart'"/>
      <!-- Bootstrap Speed Dial Replacement -->
      <div class="position-fixed bottom-0 end-0 p-3" v-if="speedDials">
        <div class="dropdown dropup">
          <button class="btn btn-primary rounded-circle p-3 utility-float-icon" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="width: 56px; height: 56px;">
            <i class="bi bi-list"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" @click.prevent="cancelFilter" data-bs-toggle="tooltip" data-bs-placement="left" title="Cancel Filter">
                <i class="bi bi-search-heart utility-color me-2"></i>
                <span>Cancel Filter</span>
              </a>
            </li>
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" @click="showFilterBox" data-bs-toggle="tooltip" data-bs-placement="left" title="Filter">
                <i class="bi bi-search utility-color me-2"></i>
                <span>Filter</span>
              </a>
            </li>
            <li>
              <a class="dropdown-item d-flex align-items-center" href="#" @click.prevent="showIntro(true)" data-bs-toggle="tooltip" data-bs-placement="left" title="Replay Tips">
                <i class="bi bi-info-circle utility-color me-2"></i>
                <span>Replay Tips</span>
              </a>
            </li>
            <li v-if="authenticated !== undefined">
              <a class="dropdown-item d-flex align-items-center" href="#" @click.prevent="newChart" data-bs-toggle="tooltip" data-bs-placement="left" title="Create New Chart">
                <i class="bi bi-plus-circle utility-color me-2"></i>
                <span>Create New Chart</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue';
  import vizGrid from '../../../gallery/app/components/Vizgrid.vue';
  import { EventServices } from '../../../../modules';
  export default Vue.component('vega-gallery', {
    data() {
      return {
        filter: false,
        bottomPosition:'bottom-0 end-0',
        speedDials: EventServices.speedDials,
        authenticated: EventServices.authUser,
        existingBkmk: {
          status: false
        }
      }
    },
    components: {
      vizGrid
    },
    mounted() {
      return this.showIntro();
    },
    methods: {
      showIntro(arg){
        return EventServices.tipController(arg)
      },
      showFilterBox () {
        EventServices.$emit('open-filter-box', {open: true, type: "filter"});
        return this.filter = true
      },
      newChart(){
        return EventServices.navTo("new", true)
      },
      cancelFilter(){
        return EventServices.cancelChartFilter();
      }
    },
    created() {
      EventServices
      .$on('close-filter-box', (data) => this.filter = data)
      .$on('isauthenticated', (data) => this.authenticated = data)
      .$on('gotexistingbookmarks', data => this.existingBkmk = data)
    }
  })
</script>
