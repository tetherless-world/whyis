
<template>
  <div>
    <div class="utility-content__result">
      <div
        class="utility-gridicon-single"
        v-if="!loading"
      >
        <div>
          <md-button
            class="md-icon-button"
            @click.native.prevent="saveAsChart"
            v-if="voyagerSpec"
          >
            <md-tooltip
              class="utility-bckg"
              md-direction="bottom"
            >
              Save current spec as new chart
            </md-tooltip>
            <md-icon>save</md-icon>
          </md-button>
          <md-button
            class="md-icon-button"
            @click.native.prevent="goToChartView"
          >
            <md-tooltip
              class="utility-bckg"
              md-direction="bottom"
            > Return to chart view </md-tooltip>
            <md-icon>arrow_back</md-icon>
          </md-button>
        </div>
      </div>
    </div>
    <div class="viz-sample__header viz-u-mgbottom">
      <span class="dv-title">Data Voyager</span><span v-if="chart && chart.title">: {{chart.title}}</span>
    </div>
    <div
      class="loading-dialog"
      style="margin: auto"
      v-if="loading"
    >
      <spinner :loading="loading" />
    </div>
    <div
      class="loading-dialog"
      style="margin: auto"
      v-else
    >
      <data-voyager
        :data="data"
        v-bind:spec.sync="voyagerSpec"
      ></data-voyager>
    </div>
  </div>
</template>

<script>
import { Slug } from "../../../../modules";
import {
  copyChart,
  loadChart,
  saveChart,
  buildSparqlSpec
} from "../../../../utilities/vega-chart";
import { querySparql } from "../../../../utilities/sparql";
import { DEFAULT_VIEWS, goToView } from "../../../../utilities/views";

export default {
  data() {
    return {
      loading: true,
      chart: null,
      voyagerSpec: null,
      specJsonEditorOpts: {
        mode: "code",
        mainMenuBar: false
      }
    };
  },
  methods: {
    slugify: Slug,
    loadChart() {
      this.loading = true;
      loadChart(this.pageUri)
        .then(chart => {
          this.chart = chart;
          return querySparql(chart.query);
        })
        .then(sparqlResults => {
          const spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults);
          this.data = spec.data;
        })
        .finally(() => (this.loading = false));
    },
    saveAsChart() {
      this.loading = true;
      const newChart = copyChart(this.chart);
      newChart.title = `DataVoyager Variant: ${newChart.title}`;
      newChart.baseSpec = this.voyagerSpec;
      console.log(newChart);
      delete newChart.depiction;
      saveChart(newChart).then(() =>
        goToView(newChart.uri, DEFAULT_VIEWS.EDIT)
      );
    },
    goToChartView() {
      goToView(this.pageUri, DEFAULT_VIEWS.VIEW);
    }
  },
  mounted() {
    this.loadChart();
  }
};
</script>

<style scoped lang="scss" src="../../../../assets/css/main.scss"></style>

<style scoped>
.dv-title {
  font-weight: 500;
}
.utility-gridicon-single {
  top: 0.5rem;
}
</style>

<style>
#voyager-embed {
  background: #fafafa;
  height: 100%;
  width: calc(100% - 2.6rem);
  margin: 30px 1.3rem;
}
</style>
