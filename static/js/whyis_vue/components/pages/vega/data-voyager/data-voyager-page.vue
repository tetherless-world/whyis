
<template>
  <div>
    <div class="viz-sample__header viz-u-mgbottom">
      Voyager
    </div>
    <div class="md-headline viz-u-mgup-sm btn--animated" v-if="chart && chart.title">{{chart.title}}</div>
    <div class="loading-dialog" style="margin: auto" v-if="loading">
      <spinner :loading="loading" />
    </div>
    <div class="loading-dialog" style="margin: auto" v-else>
      <data-voyager :data="data"></data-voyager>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue'

  import { loadChart, buildSparqlSpec } from '../../../../utilities/vega-chart'
  import { querySparql } from '../../../../utilities/sparql'

  export default {
    data () {
      return {
        loading: true,
        chart: null,
      }
    },
    methods: {
      loadChart () {
        this.loading = true
        loadChart(this.pageUri)
          .then(chart => {
            this.chart = chart
            return querySparql(chart.query)
          })
          .then(sparqlResults => {
            const spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
            this.data = spec.data
          })
          .finally(() => this.loading = false)
      },
    },
    mounted() {
      this.loadChart()
    }
  };
</script>
