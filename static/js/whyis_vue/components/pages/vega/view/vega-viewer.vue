<template>
  <div>
    <div class="utility-content__result">
      <div class="utility-gridicon-single" v-if="!loading">
        <div v-if="!vizOfTheDay">
          <md-button class="md-icon-button" @click.native.prevent="navBack">
            <md-tooltip class="utility-bckg" md-direction="bottom"> Go Back </md-tooltip>
            <md-icon>arrow_back</md-icon>
          </md-button>
        </div>
        <div>
          <md-button class="md-icon-button" @click.native.prevent="shareChart"> 
            <md-tooltip class="utility-bckg" md-direction="top"> Share Chart </md-tooltip>
            <md-icon>share</md-icon>
          </md-button>
        </div>
        <div>
          <md-button class="md-icon-button" @click.native.prevent="chartQuery"> 
            <md-tooltip class="utility-bckg" md-direction="bottom"> Preview Chart Query </md-tooltip>
            <md-icon>preview</md-icon>
          </md-button>
        </div>
        <div v-if="allowEdit">
          <md-button class="md-icon-button" @click.native.prevent="editChart"> 
            <md-tooltip class="utility-bckg" md-direction="top"> Edit Chart </md-tooltip>
            <md-icon>edit</md-icon>
          </md-button>
        </div>
      </div>
    </div>
    <div class="viz-3-col viz-u-mgup-sm">
      <div class="loading-dialog__justify">
        <div class="viz-sample">
          <div class="viz-sample__header viz-u-mgbottom" v-if="vizOfTheDay">
            <md-icon style="font-size: 2rem !important; color: gray !important">bar_chart</md-icon> Viz of the day
          </div>
          <div class="viz-u-mgbottom-big viz-u-display__desktop" v-else> </div>
          <div class="viz-sample__header viz-u-mgbottom" v-if="!vizOfTheDay">
            Chart Information
          </div>
          <div class="viz-sample__content">
            <temp-filler class="viz-sample__loading viz-sample__loading_anim" v-if="loading" />
            <div class="" v-else>
              <div class="md-headline viz-u-mgup-sm btn--animated">{{chart.title}}</div>
              <div class="btn--animated">
                {{ slugify(chart.description) }}
              </div>
              <div class="viz-sample__list btn--animated">
                <ul>
                  <li class="viz-u-postion__rel" v-for="(tag, index) in chartTags" :key="index">
                    <div class="viz-sample__content__card viz-u-display__hide viz-u-postion__abs">
                      {{ tag.description }}
                      <div><a class="btn-text btn-text--simple" target="_blank" :href="tag.uri">More</a></div>
                    </div>
                    {{ tag.title }}
                  </li>
                </ul>
              </div>
              <a @click.prevent="navBack(true)" class="btn btn_medium btn--primary viz-u-display__desktop btn--animated" v-if="!vizOfTheDay">View Gallery</a>
            </div>
          </div>
        </div>
      </div>
      <div class="loading-dialog" style="margin: auto" v-if="loading">
        <spinner :loading="loading" />
      </div>
      <div class="loading-dialog" style="margin: auto" v-else>
        <div class="viz-u-display__desktop" style="margin-bottom: 2rem"></div>
        <vega-lite :spec="spec" class="btn--animated"/>
        <a @click.prevent="navBack" class="btn btn_small btn--primary utility-margin-big viz-u-display__ph">View Gallery</a>
      </div>
    </div>
  </div>
</template>
<style scoped lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import { EventServices, Slug } from '../../../../modules'
  import tempFiller from '../../../utils/temporary_filler'
  import { loadChart, buildSparqlSpec } from '../../../../utilities/vega-chart'
  import { querySparql } from '../../../../utilities/sparql'
  import { goToView } from '../../../../utilities/views'
  export default Vue.component('vega-viewer', {
    data() {
      return {
        error: {status: false, message: null},
        filter: false,
        loading: true,
        spec: null,
        chart: null,
        chartTags: [],
        args: null,
        authenticated: EventServices.authUser,
        allowEdit: false,
        vizOfTheDay: EventServices.vizOfTheDay
      }
    },
    components: {
      tempFiller
    },
    methods: {
      loadVisualization () {
        loadChart(this.pageUri)
          .then(chart => {
            this.chart = chart
            EventServices.checkIfEditable(this.chart.uri)
            return querySparql(chart.query)
          })
          .then(sparqlResults => {
            this.spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
          })
          .finally(() => this.loading = false)
      },
      navBack(args){
        if(args) {
          EventServices.vizOfTheDay = false
        }
        return EventServices.navTo('view', true)
      },
      shareChart() {
        return EventServices.$emit("dialoguebox", {status: true, share: true, 
        title: "Share Chart", 
        message: "Copy the chart link above to share this chart", 
        chart: this.chart.uri})
      },
      editChart(){
        return goToView(this.chart.uri, 'edit')
      },
      chartQuery(){
        if(this.chart.query){
          return EventServices.$emit("dialoguebox", {status: true, query: true, title: "Chart Query", message: "Copy and rerun query on a sparql endpoint", chart: this.chart.query})
        }
      },
      slugify(args){
        return Slug(args)
      }
    },
    beforeMount(){
      return this.loadVisualization()
    },
    destroyed() {
      this.error = { status: false, message: null}
    },
    created () {
      this.loading = true;
      EventServices
      .$on('isauthenticated', (data) => this.authenticated = data)
      .$on('allowChartEdit', (data) => this.allowEdit = data)
      .$on('vizofdd', (data) => this.vizOfTheDay = data)
    }
  })
</script>