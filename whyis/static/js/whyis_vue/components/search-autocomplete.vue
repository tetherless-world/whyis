<template>
  <div class="position-relative">
    <autocomplete 
      v-model="selected" 
      :fetch-data="resolveEntity"
      :display-field="'prefLabel'"
      :key-field="'node'"
      @select="selectedItemChange"
      placeholder="Search knowledge base..."
      input-class="form-control-lg"
      :min-chars="3">
      <template #option="{ item }">
        <div>
          <span>{{ item.prefLabel || item.label }}</span>
          <span v-if="item.label && item.label !== item.prefLabel" class="text-muted ms-1">({{ item.label }})</span>
        </div>
      </template>
      <template #selected="{ item }">
        <span>{{ item.prefLabel || item.label }}</span>
      </template>
    </autocomplete>
  </div>
</template>

<script>
import Vue from "vue";
import axios from 'axios';

export default Vue.component('search-autocomplete', {
    data: () => ({
      selected: null
    }),
    methods: {
        async resolveEntity(query) {
            if (query && query.length > 2) {
                try {
                    const response = await axios.get('/', {
                        params: { view: 'resolve', term: query + "*" },
                        responseType: 'json'
                    });
                    return response.data || [];
                } catch (error) {
                    console.error('Error resolving entities:', error);
                    return [];
                }
            } else {
                return [];
            }
        },
        selectedItemChange(item) {
            if (item && item.node) {
                window.location.href = '/about?view=view&uri=' + encodeURIComponent(item.node);
            }
        }
    },
    props: ['root_url', 'axios']
});
</script>
