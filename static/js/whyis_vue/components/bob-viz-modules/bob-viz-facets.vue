<template>
  <div class="bob-viz-facets">
    <div class="md-layout">
        <md-field class="md-layout-item">
            <label>Class URI</label>
            <md-input name="class-uri" id="class-uri" v-model="uriInput"/>
        </md-field>      
        <div class="md-layout-item" style="max-width:fit-content">
        <md-button class="md-icon-button md-raised" @click="setBrowserUri">
            <md-icon> arrow_forward </md-icon>
            <md-tooltip md-direction="top">Submit URI to browser</md-tooltip>
        </md-button>
        </div> 
    </div>
    <facet-browser v-bind:class_uri="facetClassUri" 
        :key="facetClassUri" 
        v-bind:show_yasr="false" 
        @facet-browser-update="onQuerySuccess"/>
  </div>
</template>

<script>
import Vue from "vue";
import { mapActions } from 'vuex';

export default Vue.component('bob-viz-facets', {
  data: () => ({
    query: null,
    uriInput: "",
    facetClassUri: {
        type: String,
        default: "http://materialsmine.org/ns/Metamaterial"
    },
  }),
  methods: {
    ...mapActions('bobViz', ['setResults', 'setQuery']),
    onQuerySuccess(results) {
      this.query = results.fbquery;
      this.setResults(results.fbresults)
    },
    setBrowserUri(){
      this.facetClassUri = this.uriInput;
    },
  },
  watch: {
    query(query) {
      this.setQuery(query)
    }
  }
})
</script>