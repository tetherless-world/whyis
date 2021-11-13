<template>
<div class="">
    <div class="viz-editor-tabs" @click="showTabNavigation">
        <div class="viz-editor-tabs-item" id="tableResultsE" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Table
        <md-tooltip md-direction="bottom">View results as table</md-tooltip>
        </div>
        <div class="viz-editor-tabs-item" id="vegaE" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Vega
        <md-tooltip md-direction="bottom">Enter Vega Specs</md-tooltip>
        </div>
        <div class="viz-editor-tabs-item tabselected" id="dataVoyagerE" @click="tabNavigation" :style="showAllTabBtn ? showAllTabs : false">
        Data Voyager
        <md-tooltip md-direction="bottom">Explore with Data Voyager</md-tooltip>
        </div>
    </div>
     <div class="viz-editor" id="tableResultsc">
        <bob-viz-results/>
     </div>
     <div class="viz-editor" id="vegac">
        <bob-viz-vega/>
     </div>
     <div class="viz-editor viz-editor-show" id="dataVoyagerc">
        <bob-viz-voyager/>
     </div>
</div>
</template>
<style scoped lang="scss" src="../../assets/css/main.scss"></style>
<script>
import Vue from 'vue';

import { mapGetters } from 'vuex';
export default Vue.component('bob-viz-tabular-explore', {
  data() {
    return {
      showAllTabBtn: false,
      showAllTabs: {display: 'none'},
    }
  },
  computed: {
    ...mapGetters('bobViz', ['results', 'vegaData'])
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
      const tableResults = document.getElementById('tableResultsc')
      const vega = document.getElementById('vegac')
      const dataVoyager = document.getElementById('dataVoyagerc')
      const tabs = await document.querySelectorAll('.viz-editor-tabs-item')
      if(tabs.length){
        [].forEach.call(tabs, function(el) {
            el.classList.remove('tabselected')})
      }
      e.srcElement.classList.add('tabselected')
      if(e.srcElement.id == 'vegaE'){
        tableResults.classList.remove('viz-editor-show')
        dataVoyager.classList.remove('viz-editor-show')
        vega.classList.add('viz-editor-show')
      } else if(e.srcElement.id == 'dataVoyagerE') {
        tableResults.classList.remove('viz-editor-show')
        vega.classList.remove('viz-editor-show')
        dataVoyager.classList.add('viz-editor-show')
      } else {
        vega.classList.remove('viz-editor-show')
        dataVoyager.classList.remove('viz-editor-show')
        tableResults.classList.add('viz-editor-show')
      }
    },
  }
})
</script>
