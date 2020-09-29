<template>
  <div>
    <div v-if="loading">
      <spinner :loading="loading" :text='loadingText'/>
    </div>
    <div v-else>
     <div class=""></div>
      <md-speed-dial :class="bottomPosition" v-if="speedDials">
        <md-speed-dial-target class="utility-float-icon">
          <md-icon>menu</md-icon>
        </md-speed-dial-target>

        <md-speed-dial-content>
          <md-button class="md-icon-button" @click.prevent="cancelFilter">
            <md-tooltip class="utility-bckg" md-direction="left"> Cancel Filter </md-tooltip>
            <md-icon class="utility-color">search_off</md-icon>
          </md-button>
          <md-button class="md-icon-button" @click="null">
            <md-tooltip class="utility-bckg" md-direction="left"> Filter </md-tooltip>
            <md-icon class="utility-color">search</md-icon>
          </md-button>
          <md-button class="md-icon-button" v-if="authenticated !== undefined" @click.prevent="null">
            <md-tooltip class="utility-bckg" md-direction="left">Create New Chart</md-tooltip>
            <md-icon class="utility-color">add</md-icon>
          </md-button>
        </md-speed-dial-content>
      </md-speed-dial>
    </div>
  </div>
</template>
<style scoped lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue';
  import EventServices from '../../../../modules/events/event-services';
  export default Vue.component('vega-dataset', {
    data() {
      return {
        filter: false,
        bottomPosition:'md-bottom-right',
        speedDials: EventServices.speedDials,
        authenticated: EventServices.authUser,
        loading: false,
        loadingText: "Loading Existing Datasets"
      }
    },
    methods: {
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
    mounted(){
        this.loading = true,
        setTimeout(() => {
            this.loading = false
        }, 2000)
    },
    created() {
      EventServices
      .$on('close-filter-box', (data) => this.filter = data)
      .$on('isauthenticated', (data) => this.authenticated = data)
    }
  })
</script>
