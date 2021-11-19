<template>
<div class="">
    <div class="viz-editor-tabs" @click="showTabNavigation">
        <div v-if="tableResults.show" class="viz-editor-tabs-item" id="tableResults" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Table
        <md-tooltip md-direction="bottom">View results as table</md-tooltip>
        </div>
        <div v-if="vegaLite.show" class="viz-editor-tabs-item" id="vegaLite" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Vega
        <md-tooltip md-direction="bottom">Enter Vega Specs</md-tooltip>
        </div>
        <div v-if="dataVoyager.show" class="viz-editor-tabs-item" id="dataVoyager" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Data Voyager
        <md-tooltip md-direction="bottom">Explore with Data Voyager</md-tooltip>
        </div>
    </div>
     <div v-if="tableResults.show" class="viz-editor" id="tableResultsC">
        <bob-viz-results/>
     </div>
     <div v-if="vegaLite.show" class="viz-editor" id="vegaLiteC">
        <bob-viz-vega/>
     </div>
     <div v-if="dataVoyager.show" class="viz-editor" id="dataVoyagerC">
        <bob-viz-voyager/>
     </div>
</div>
</template>
<style scoped lang="scss" src="../../assets/css/main.scss"></style>
<script>
import Vue from 'vue';
 
export default Vue.component('bob-viz-tabular-explore', {
  props: {
    component_array: {
      type: Array,
      default: () => ['tableResults', 'vegaLite', 'dataVoyager']
    },
  },
  data() {
    return {
      tableResults: {
        show: false,
        compId: 'tableResultsC',
      },
      vegaLite: {
        show: false,
        compId: 'vegaLiteC',
      },
      dataVoyager: {
        show: false,
        compId: 'dataVoyagerC',
      },
      showAllTabBtn: false,
      showAllTabs: {display: 'none'},
    }
  }, 
  methods: {
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
      const tabs = await document.querySelectorAll('.viz-editor-tabs-item')
      if(tabs.length){
        [].forEach.call(tabs, function(el) {
            el.classList.remove('tabselected')})
      }
      e.srcElement.classList.add('tabselected')
      const components = await document.querySelectorAll('.viz-editor')
      if(components.length){
        [].forEach.call(components, function(el) {
            el.classList.remove('viz-editor-show')})
      }
      if (this[e.srcElement.id]){
        const showComponent = document.getElementById(this[e.srcElement.id]['compId'])
        showComponent.classList.add('viz-editor-show')
      }
    },
  },
  created: function () {
    let this_vue = this
    if(this_vue.component_array.length){
      [].forEach.call(this_vue.component_array, function(el) {
        if (this_vue[el]){
          this_vue[el]['show'] = true}
        }) 
    }
  },
  mounted: function () {
    let showId = this.component_array[0]
    let showTab = document.getElementById(showId)
    showTab.classList.add('tabselected')
    let showComponent = document.getElementById(this[showId]['compId'])
    showComponent.classList.add('viz-editor-show')
  }
})
</script>
