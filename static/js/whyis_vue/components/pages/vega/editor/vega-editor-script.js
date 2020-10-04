import Vue from 'vue'
import { EventServices } from '../../../../modules'
import splitPane from 'vue-splitpane'
import VJsoneditor from 'v-jsoneditor'
import { getDefaultChart, loadChart, saveChart, buildSparqlSpec } from 'utilities/vega-chart'
import { getCurrentView } from 'utilities/views'
import { querySparql } from 'utilities/sparql'

export default Vue.component('vega-editor', {
  props:['instances'],
  data() {
    return {
      loading: false,
      showAllTabBtn: false,
      showAllTabs: {display: 'none'},
      paneResize: 18,
      bottomPosition:'md-bottom-right',
      previewPane: true,
      authenticated: EventServices.authUser,
      restoredChartId: null,
      chart: {
        baseSpec: null,
        query: null,
        title: null,
        description: null
      },
      results: null,
      chartPub: null,
      specJsonEditorOpts: {
        mode: 'code',
        mainMenuBar: false
      },
      actionType: 'Save Chart'
    }
  },
  computed: {
    spec () {
      const spec = buildSparqlSpec(this.chart.baseSpec, this.results)
      return spec
    }
  },
  components: {
    splitPane,
    VJsoneditor
  },
  methods: {
    navBack(){
      return EventServices.navTo('view', true)
    },
    resize(e){
      if(e <= 26){
        this.showAllTabBtn = true;
      } else {
        this.showAllTabBtn = false;
      }
    },
    showTabNavigation(){
      this.paneResize = 50;
      this.showAllTabBtn = false;
      return this.paneResize = 18;
    },
    async tabNavigation(e){
      const sparql = document.getElementById('sparqlc')
      const vega = document.getElementById('vegac')
      const save = document.getElementById('savec')
      const tabs = await document.querySelectorAll('.viz-editor-tabs-item')
      if(tabs.length){
        tabs.forEach(el => el.classList.remove('tabselected'))
      }
      e.srcElement.classList.add('tabselected')
      if(e.srcElement.id == 'vegaE'){
        sparql.classList.remove('viz-editor-show')
        save.classList.remove('viz-editor-show')
        vega.classList.add('viz-editor-show')
      } else if(e.srcElement.id == 'saveE') {
        sparql.classList.remove('viz-editor-show')
        vega.classList.remove('viz-editor-show')
        save.classList.add('viz-editor-show')
      } else {
        save.classList.remove('viz-editor-show')
        vega.classList.remove('viz-editor-show')
        sparql.classList.add('viz-editor-show')
      }
    },
    getSparqlData () {
      const vm = this;
      querySparql(vm.chart.query)
        .then(this.onQuerySuccess)
        .then(() => this.loading = false)
    },
    onQuerySuccess (results) {
      this.results = results
    },
    onSpecJsonError () {
      console.log('bad', arguments)
    },
    async onNewVegaView (view) {
      const blob = await view.toImageURL('png')
        .then(url => fetch(url))
        .then(resp => resp.blob())
      const fr = new FileReader()
      fr.addEventListener('load', () => {
        this.chart.depiction = fr.result
      })
      fr.readAsDataURL(blob)
    },
    loadChart () {
      let getChartPromise
      if (this.pageView === 'new') {
        getChartPromise = Promise.resolve(getDefaultChart())
      } else {
        getChartPromise = loadChart(this.pageUri)
      }
      getChartPromise
        .then(chart => {
          this.chart = chart
          this.getSparqlData()
        })
    },
    async reloadRestored(args){
      const currChart = EventServices.tempChart;
      if(currChart && currChart.chart){
        await ec.appState.filter(el => {
          if(el._id == currChart.chart._id) {
            el.restored = true;
          }
        })
      }
      const text = args == 'Editing' ? 'Edited' : 'Restored'
      EventServices.$emit('snacks', {status:true, message: `Chart ${text} Successfully`});
      //RELOAD RESTORE USED IN SETTINGS TO RE FILTER CHART LIST
      EventServices.$emit('reloadrestored', true)
      return EventServices.navTo('view', true);
    },
    async saveChart () {
      const vm = this;
      try {
        saveChart(this.chart)
        .then(async() => {
          if(vm.actionType == 'Restore' || vm.actionType == 'Editing'){
            const res = await EventServices.createBackUp(vm.chart, vm.restoredChartId, true, this.selectedTags);
            if(res.mssg){
              return vm.reloadRestored(vm.actionType);
            }
            return;
          } else {
            await EventServices.createBackUp(this.chart, null, true, this.selectedTags);
            EventServices.$emit('snacks', {status:true, message: 'Chart Saved Successfully'});
            return EventServices.navTo('view', true);
          }
        })
      } catch(err){
        //TODO USE THE APP DIALOGUE BOX INSTEAD OF ALERT BOX
        return alert(err)
      }
    },
    postChartBk(){
      let recievedChart = EventServices.tempChart;
      if(!recievedChart){
        return;
      } else {
        this.chart.baseSpec = recievedChart.chart.backup.baseSpec
        this.chart.query = recievedChart.chart.backup.query
        this.chart.title = recievedChart.chart.backup.title
        this.chart.description = recievedChart.chart.backup.description
        this.restoredChartId = recievedChart.chart.name
      }
    },
    defineAction(){
      const thisView = getCurrentView();
      if(thisView == 'restore'){
        this.actionType = 'Restore';
      } else if (thisView == 'edit'){
        this.actionType = 'Editing';
      } else {
        this.actionType = 'Save Chart';
      }
    },
  },
  created () {
    if(EventServices.authUser == undefined){
      return EventServices.navTo('view', true)
    }
    this.loading = true;
    this.defineAction();
    this.postChartBk();
    this.loadChart();
  }
})
