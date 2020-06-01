<template>
 <div class="page-container">
    <md-app md-waterfall md-mode="overlap">
      <md-app-toolbar />
      <md-app-drawer />
      <md-app-content>
        <div class="utility-content__result">Home > Single Chart > <span class="utility-color"><strong>{{ title }}</strong></span></div>
        <vega-lite :spec="spec"/>
      </md-app-content>
    </md-app>
    <md-speed-dial :class="bottomPosition" @click.native.prevent="navBack">
      <md-speed-dial-target class="utility-float-icon">
        <md-icon>arrow_back</md-icon>
      </md-speed-dial-target>
    </md-speed-dial>
  </div>
</template>
<style scoped lang="scss" src="../static/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import { eventCourier as ec } from '../store'
  import Header from './header/Header'
  import Drawer from './header/Drawer'
  import { loadChart, buildSparqlSpec } from '../../../../utilities/vega-chart'
  import { querySparql } from '../../../../utilities/sparql'
  import { router } from '../router/routes'

  export default Vue.component('single', {
    mixins: [router],
    props:{
      passedargs: {
        type: Object,
        require: true,
        default: () => {
          return {}
        }
      }
    },
    data() {
      return {
        menuVisible: false,
        filter: false,
        bottomPosition:'md-bottom-right',
        loading: true,
        spec: null,
        chart: null,
        args: null
      }
    },
    components: {
      mdAppToolbar: Header,
      mdAppDrawer: Drawer
    },
    methods: {
      loadVisualization () {
        console.log(this.args)
        this.loading = true
        loadChart(this.pageUri)
          .then(chart => {
            this.chart = chart
            return querySparql(chart.query)
          })
          .then(sparqlResults => {
            this.spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
            console.log(this.spec)
          })
          .finally(() => this.loading = false)
      },
      navBack(){
        return this.goBack()
      }
    },
    created () {
      ec.$on("route-args", (data) => this.args=data)
      this.loadVisualization()
    }
  })
</script>