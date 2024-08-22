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
        <div v-if="chart.query">
          <md-button class="md-icon-button" @click.native.prevent="chartQuery">
            <md-tooltip class="utility-bckg" md-direction="bottom"> Preview Chart Query </md-tooltip>
            <md-icon>preview</md-icon>
          </md-button>
        </div>
        <div>
          <md-button class="md-icon-button" @click.native.prevent="tableView">
            <md-tooltip class="utility-bckg" md-direction="bottom"> View Data as Table </md-tooltip>
            <md-icon>table_view</md-icon>
          </md-button>
        </div>
        <div>
          <md-button class="md-icon-button" @click.native.prevent="specViewer.show = true">
            <md-tooltip class="utility-bckg" md-direction="bottom"> Preview Chart Spec </md-tooltip>
            <md-icon>integration_instructions</md-icon>
          </md-button>
        </div>
        <div>
          <md-button class="md-icon-button" @click.native.prevent="openVoyager()">
            <md-tooltip class="utility-bckg" md-direction="bottom"> View Data in Voyager </md-tooltip>
            <md-icon>dynamic_form</md-icon>
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
              <a @click.prevent="navBack(true)" class="btn btn_medium btn--primary viz-u-display__desktop btn--animated" v-if="vizOfTheDay">View Gallery</a>
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
        <a @click.prevent="navBack(true)" class="btn btn_small btn--primary utility-margin-big viz-u-display__ph" v-if="vizOfTheDay">View Gallery</a>
      </div>
      <md-dialog :md-active.sync="specViewer.show" class="chart-spec">
        <md-dialog-title>Chart Vega Spec</md-dialog-title>
        <md-content class="vega-spec-container">
          <v-jsoneditor
            v-model="specViewerSpec"
            :options="specViewer.jsonEditorOpts"
          >
          </v-jsoneditor>
        </md-content>
        <div class="vega-spec-controls">
          <md-checkbox v-model="specViewer.includeData">Include data in spec</md-checkbox>
        </div>
        <md-dialog-actions>
          <md-button class="md-primary" @click="specViewer.show = false">Close</md-button>
        </md-dialog-actions>
      </md-dialog>
      <data-voyager v-if="voyager.show" :data="spec.data"></data-voyager>
    </div>
  </div>
</template>
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<style scoped lang="scss">

  .vega-spec-container {
    padding-left: 20px;
    padding-right: 20px;
    height: 600px;
    max-height: 100%;
    width: 724px;
    max-width: 100%;
  }
  .vega-spec-controls {
    padding-left: 20px;
    padding-right: 20px;
  }
</style>
<script>
  import Vue from 'vue'
  import VJsoneditor from 'v-jsoneditor'

  import { EventServices, Slug } from '../../../../modules'
  import tempFiller from '../../../utils/temporary_filler.vue'
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
        vizOfTheDay: false,
        voyager: {
          show: false
        },
        specViewer: {
          show: false,
          includeData: false,
          jsonEditorOpts: {
            mode: 'code',
            mainMenuBar: false,
            onEditable: () => false,
          },
        }
      }
    },
    components: {
      tempFiller,
      VJsoneditor,
    },
    computed: {
      specViewerSpec () {
        return this.specViewer.includeData ? this.spec : this.chart && this.chart.baseSpec
      }
    },
    methods: {
      async loadVisualization () {
        this.chart = await loadChart(this.pageUri)
        EventServices.checkIfEditable(this.chart.uri)
        if (this.chart.query) {
          const sparqlResults = await querySparql(this.chart.query)
          this.spec = buildSparqlSpec(this.chart.baseSpec, sparqlResults)
        } else {
          this.spec = this.chart.baseSpec
        }
        if (this.chart.dataset) {
          this.spec = this.chart.baseSpec
          this.spec.data = {url: `/about?uri=${this.chart.dataset}`}
        }
        this.loading = false
      },
      navBack(args){
        if(args) {
          EventServices.toggleVizOfTheDay(args)
        }
        return EventServices.navTo('view', true)
      },
      openVoyager() {
        goToView(this.chart.uri, 'voyager')
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
          return EventServices.$emit("dialoguebox", {status: true, query: true, 
          title: "Chart Query", 
          message: "Copy and rerun query on a sparql endpoint", 
          chart: this.chart.query})
        }
      },
      slugify(args){
        return Slug(args)
      },
      tableView(){
        if(this.chart.query){
          querySparql(this.chart.query)
          .then(sparqlResults => {
            console.log(sparqlResults)
            return EventServices.$emit("dialoguebox", {status: true, 
              tableview: sparqlResults, 
              title: "Table View of Chart Data",
              chart: this.chart.query})
          })
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
    }
  })
</script>
