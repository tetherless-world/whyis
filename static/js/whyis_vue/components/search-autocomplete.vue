<template>
<md-autocomplete
   class="search"
   md-input-name="query"
   :md-options="items"
   md-layout="box"
   v-model="selectedItem"
   @md-changed="resolveEntity"
   md-selected="selectedItemChange">
  <label>Search</label>
  <template slot="md-autocomplete-item" slot-scope="{item}">
    <span md-term="searchText" md-fuzzy-search="true">{{item.label}}</span>
    <span v-if="item.label != item.preflabel">(preferred: {{item.preflabel}})</span>
    <span v-if="item.types.length > 0">
      (<span v-for="t in item.types">{{t.label}}</span><span ng-if="!$last">, </span>)
    </span>
  </template>
  <input type="hidden" name="search" v-model="query"/>
</md-autocomplete>
</template>

<script>
import Vue from "vue";
import axios from 'axios';

export default Vue.component('search-autocomplete', {
    data: () => ({
      query: null,
      selectedItem: null,
      items: []
    }),
    methods: {
        resolveEntity (query) {
            this.items = axios.get('/',{params:{view:'resolve',term:query+"*"},
                                 responseType:'json' })
                .then(function(response) {
                    return response.data;
                });
        },
        selectedItemChange(item) {
            window.location.href = '/'+'about?uri='+window.encodeURIComponent(item.node);
        }
    },
    props: ['root_url', 'axios']
});
</script>
