<template>
  <div class="page-container">
    <md-app md-waterfall md-mode="overlap">
      <md-app-toolbar :authenticated="authenticated" />
      <md-app-drawer :authenticated="authenticated" :globalargs="globalargs" />
      <md-app-content>
        <div class="utility-content__result">Home > Single Chart > <span class="utility-color"><strong>{{ args.label }}</strong></span></div>
        <div class="loading-dialog" v-if="loading">
          <div class="md-title">Loading {{ args.label }}...</div>
          <md-progress-spinner class="md-primary"
                                :md-diameter="200"
                                :md-stroke="20"
                                md-mode="indeterminate">
          </md-progress-spinner>
        </div>
        <div class="loading-dialog" v-else>
          <div class="md-subheading">{{args.label}}</div>
          <vega-lite :spec="spec" />
          <div class="utility-margin"><span><strong>Chart Description:</strong></span>{{ args.description}}</div>
        </div>
      </md-app-content>
    </md-app>
    <md-speed-dial :class="bottomPosition" >
      <md-speed-dial-target class="utility-float-icon" @click.native.prevent="navBack">
        <md-icon>arrow_back</md-icon>
      </md-speed-dial-target>
       <md-speed-dial-target class="utility-float-icon">
        <md-icon>share</md-icon>
      </md-speed-dial-target>
    </md-speed-dial>
  </div>
</template>
<style scoped lang="scss" src="../static/css/main.scss"></style>
<script>
  import { eventCourier as ec, state } from '../store'
  import Header from './header/Header'
  import Drawer from './header/Drawer'
  import { router } from '../router/routes'
  import { loadChart, buildSparqlSpec } from '../../../../utilities/vega-chart'
  import { querySparql } from '../../../../utilities/sparql'
  import { getViewUrl } from '../../../../utilities/views'

  export default {
    name: 'single',
    mixins: [router],
    props:{
      globalargs: {
        type: String
      }
    },
    data() {
      return {
        // menuVisible: false,
        filter: false,
        bottomPosition:'md-bottom-right',
        loading: true,
        spec: null,
        chart: null,
        args: state.appRoutes.pageArgs[0],
        authenticated: ec.authenticated,
      }
    },
    components: {
      mdAppToolbar: Header,
      mdAppDrawer: Drawer
    },
    methods: {
      loadVisualization () {
        this.loading = true;
        loadChart(this.args.identifier)
          .then(chart => {
            this.chart = chart
            return querySparql(chart.query)
          })
          .then(sparqlResults => {
            this.spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
          })
          .finally(() => this.loading = false)
      },
      navBack(){
        return this.goBack()
      }
    },
    beforeMount(){
      return this.loadVisualization()
    },
    created () {
      ec
      .$on("route-args", (data) => this.args=data)
      .$on('isauthenticated', (data) => this.authenticated = data)
    }
  }
</script>