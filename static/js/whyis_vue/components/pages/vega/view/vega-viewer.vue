<template>
  <div>
    <div class="loading-dialog" v-if="loading">
      <div class="md-title">Loading visualization...</div>
      <md-progress-spinner class="md-primary"
                            :md-diameter="200"
                            :md-stroke="20"
                            md-mode="indeterminate">
      </md-progress-spinner>
    </div>
    <div v-else class="vega-container">
      <div class="chart-metadata">
        <div class="md-title">{{chart.title}}</div>
        <p class="chart-description">{{chart.description}}</p>
        <div>
          <md-button class="md-primary md-raised"
                     title="Edit this visualization"
                     aria-label="Edit this visualization"
                     >
            <md-icon>edit</md-icon>
            Edit
          </md-button>
        </div>
      </div>
      <vega-lite :spec="spec"/>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

import { getViewUrl } from 'utilities/views'
import { loadChart, buildSparqlSpec } from 'utilities/vega-chart'
import { querySparql } from 'utilities/sparql'

export default Vue.component('vega-viewer', {
  data () {
    return {
      loading: true,
      chart: null,
      spec: null
    }
  },
  created () {
    this.loadVisualization()
  },
  computed: {
    editUrl () {
      return getViewUrl(this.pageUri, 'edit')
    }
  },
  methods: {
    loadVisualization () {
      this.loading = true
      loadChart(this.pageUri)
        .then(chart => {
          this.chart = chart
          return querySparql(chart.query)
        })
        .then(sparqlResults => {
          this.spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
        })
        .finally(() => this.loading = false)
    },
  }
});
</script>

<style scoped lang="scss">
.loading-dialog {
  text-align: center;

  .md-title {
    margin: 10em
  }
}

.vega-container {
  display: flex;
  flex-direction: column;
  align-items: center;

  .chart-metadata {
    width: 800px;
    margin: 3em;
  }
}
</style>
