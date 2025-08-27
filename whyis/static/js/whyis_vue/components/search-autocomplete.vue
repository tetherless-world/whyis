<template>
  <div class="search-autocomplete position-relative">
    <input 
      type="search" 
      class="form-control" 
      placeholder="Search" 
      name="query"
      v-model="searchText"
      @input="resolveEntity"
      @keydown.enter.prevent="handleEnter"
      @focus="showDropdown = true"
      @blur="hideDropdown"
      autocomplete="off"
    >
    <div v-if="showDropdown && items.length > 0" class="dropdown-menu show position-absolute w-100 mt-1" style="z-index: 1050;">
      <a 
        v-for="item in items" 
        :key="item.node"
        class="dropdown-item d-flex flex-column"
        href="#"
        @mousedown.prevent="selectedItemChange(item)"
      >
        <span class="fw-bold">{{item.label}}</span>
        <small v-if="item.label != item.preflabel" class="text-muted">(preferred: {{item.preflabel}})</small>
      </a>
    </div>
    <input type="hidden" name="search" v-model="query"/>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'search-autocomplete',
    data: () => ({
      query: null,
      searchText: '',
      selected: null,
      items: [],
      showDropdown: false
    }),
    methods: {
        async resolveEntity (event) {
            const query = event.target ? event.target.value : event;
            this.searchText = query;
            
            if (!query || query.length < 2) {
                this.items = [];
                this.showDropdown = false;
                return;
            }
            
            try {
                const response = await axios.get('/', {
                    params: { view: 'resolve', term: query + "*" },
                    responseType: 'json'
                });
                
                let result = response.data;
                result.forEach(function (x) {
                    x.toLowerCase = () => x.label.toLowerCase();
                    x.toString = () => x.label;
                });
                
                this.items = result;
                this.showDropdown = true;
            } catch (error) {
                console.error('Search error:', error);
                this.items = [];
                this.showDropdown = false;
            }
        },
        selectedItemChange(item) {
            this.searchText = item.label;
            this.showDropdown = false;
            window.location.href = '/' + 'about?view=view&uri=' + window.encodeURIComponent(item.node);
        },
        handleEnter() {
            if (this.items.length > 0) {
                this.selectedItemChange(this.items[0]);
            } else {
                // Submit the search form
                const form = this.$el.closest('form');
                if (form) {
                    form.submit();
                }
            }
        },
        hideDropdown() {
            // Delay hiding to allow click events to fire
            setTimeout(() => {
                this.showDropdown = false;
            }, 150);
        }
    },
    props: ['root_url', 'axios']
}
</script>
