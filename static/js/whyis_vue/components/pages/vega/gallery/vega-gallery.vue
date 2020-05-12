<template>
<div>
  <h1>Visualization Gallery Placeholder</h1>
  <h3 v-if="loading">Loading charts...</h3>
  <ul v-else-if="charts.length > 0">
    <li v-for="chart in charts" :key="chart.uri">
      {{chart.uri}} {{chart.title}}
    </li>
  </ul>
  <h3 v-else>No charts found!</h3>
</div>
</template>

<script>
import Vue from 'vue'

import { getCharts } from 'utilities/vega-chart'

export default Vue.component('vega-gallery', {
  data () {
    return {
      loading: false,
      charts: []
    }
  },
  created () {
    this.loading = true
    getCharts()
      .then((charts) => {this.charts = charts; console.log(charts)})
      .finally(() => this.loading = false)
  }
})
</script>
