<template>
  <div class="">
    <div class="utility-content__result">Home > Single Chart > <span class="utility-color"><strong>{{ args.label }}</strong></span></div>
    <div class="loading-dialog" v-if="loading">
      <spinner :loading="loading" text='loading data...'/>
    </div>
    <div class="loading-dialog" v-else>
      <div class="md-subheading">{{args.label}}</div>
      <vega-lite :spec="spec" />
      <div class="utility-margin"><span><strong>Description:</strong></span>{{ args.description}}</div>
    </div>
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
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
  import EventServices from '../../../../modules/events/event-services'
  import { loadChart, buildSparqlSpec } from '../../../../utilities/vega-chart'
  import { querySparql } from '../../../../utilities/sparql'

  export default {
    name: 'single',
    props:{
      globalargs: {
        type: String
      }
    },
    data() {
      return {
        filter: false,
        bottomPosition:'md-bottom-right',
        loading: true,
        spec: null,
        chart: null,
        authenticated: false,
        speedDials: EventServices.speedDials,
      }
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
      
    }
  }
</script>