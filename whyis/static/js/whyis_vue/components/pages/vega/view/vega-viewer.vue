<template>
  <div>
    <div class="utility-content__result">
      <div class="utility-gridicon-single" v-if="!loading">
        <div v-if="!vizOfTheDay">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="navBack" title="Go Back">
            <i class="bi bi-arrow-left"></i>
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="shareChart" title="Share Chart">
            <i class="bi bi-share"></i>
          </button>
        </div>
        <div v-if="chart.query">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="chartQuery" title="Preview Chart Query">
            <i class="bi bi-eye"></i>
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="tableView" title="View Data as Table">
            <i class="bi bi-table"></i>
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="specViewer.show = true" title="Preview Chart Spec">
            <i class="bi bi-code-slash"></i>
          </button>
        </div>
        <div v-if="allowEdit">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click.prevent="editChart" title="Edit Chart">
            <i class="bi bi-pencil"></i>
          </button>
        </div>
      </div>
    </div>
    <div class="viz-3-col viz-u-mgup-sm">
      <div class="loading-dialog__justify">
        <div class="viz-sample">
          <div class="viz-sample__header viz-u-mgbottom" v-if="vizOfTheDay">
            <i class="bi bi-bar-chart" style="font-size: 2rem !important; color: gray !important"></i> Viz of the day
          </div>
          <div class="viz-u-mgbottom-big viz-u-display__desktop" v-else> </div>
          <div class="viz-sample__header viz-u-mgbottom" v-if="!vizOfTheDay">
            Chart Information
          </div>
          <div class="viz-sample__content">
            <temp-filler class="viz-sample__loading viz-sample__loading_anim" v-if="loading" />
            <div class="" v-else>
              <h3 class="h4 viz-u-mgup-sm btn--animated">{{ chart.title }}</h3>
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
      <!-- Bootstrap Modal for Chart Spec -->
      <div class="modal fade" tabindex="-1" :class="{'show': specViewer.show}" :style="{display: specViewer.show ? 'block' : 'none'}" v-if="specViewer.show">
        <div class="modal-dialog modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Chart Vega Spec</h5>
              <button type="button" class="btn-close" @click="specViewer.show = false" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="vega-spec-container">
                <v-jsoneditor
                  v-model="specViewerSpec"
                  :options="specViewer.jsonEditorOpts"
                >
                </v-jsoneditor>
              </div>
            </div>
            <div class="modal-footer d-flex justify-content-between">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="specViewer.includeData" id="includeDataCheck">
                <label class="form-check-label" for="includeDataCheck">
                  Include data in spec
                </label>
              </div>
              <button type="button" class="btn btn-primary" @click="specViewer.show = false">Close</button>
            </div>
          </div>
        </div>
      </div>
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
