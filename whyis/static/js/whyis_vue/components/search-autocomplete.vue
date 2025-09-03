<template>
  <div class="position-relative">
    <div class="form-floating">
      <input type="text" 
             class="form-control search" 
             id="searchInput"
             v-model="selected" 
             @input="resolveEntity($event.target.value)"
             @focus="showDropdown = true"
             @blur="hideDropdown"
             placeholder="Search">
      <label for="searchInput">Search</label>
    </div>
    
    <!-- Dropdown results -->
    <div v-if="showDropdown && items.length > 0" class="dropdown-menu show position-absolute w-100" style="max-height: 300px; overflow-y: auto; z-index: 1050;">
      <button v-for="item in items" :key="item.node" 
              class="dropdown-item text-start" 
              @mousedown="selectedItemChange(item)">
        <div>
          <span>{{ item.label }}</span>
          <span v-if="item.label != item.preflabel" class="text-muted">(preferred: {{ item.preflabel }})</span>
        </div>
      </button>
    </div>
    
    <input type="hidden" name="search" v-model="query"/>
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
