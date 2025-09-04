<template>
  <div class="position-relative">
    <div class="form-floating">
      <autocomplete type="text" 
             v-model="selected" 
             :fetch-data="resolveEntity"
             key-field="label"
             @select="selectedItemChange"
             placeholder="Search">
        <template #option="{ item }">
          <div>
            <span>{{ item.prefLabel }}</span>
            <span v-if="item.label != item.preflabel" class="text-muted">(match: {{ item.label }})</span>
          </div>
        </template>
        <template #selected="{ item }">
          <div>
            <span>{{ item.prefLabel }}</span>
          </div>
        </template>
      </autocomplete>
    </div>

  </div>
</template>

<script>
import Vue from "vue";
import axios from 'axios';

export default Vue.component('search-autocomplete', {
    data: () => ({
      query: null,
      selected: null,
      items: [],
      showDropdown: false
    }),
    methods: {
        resolveEntity (query) {
            this.query = query;
            if (query && query.length > 2) {
                this.items = axios.get('/',{params:{view:'resolve',term:query+"*"},
                                     responseType:'json' })
                    .then((response) => {
                        var result = response.data;
                        result.forEach(function (x) {
                          x.toLowerCase = () => x.label.toLowerCase();
                          x.toString = () => x.label;
                        });
                        this.items = result;
                        this.showDropdown = true;
                        return result;
                    });
            } else {
                this.items = [];
                this.showDropdown = false;
            }
        },
        selectedItemChange(item) {
            this.selected = item.label;
            this.showDropdown = false;
            window.location.href = '/'+'about?view=view&uri='+window.encodeURIComponent(item.node);
        },
        hideDropdown() {
            // Use setTimeout to allow click events to fire before hiding
            setTimeout(() => {
                this.showDropdown = false;
            }, 200);
        }
    },
    props: ['root_url', 'axios']
});
</script>
