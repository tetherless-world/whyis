<template>
<div>
  <yasqe
    :value="query"
    @query-success="onQuerySuccess"
  />
    <!-- v-if="query"
    :value="query"
    :readOnly="queryEditorReadOnly"
    @input="setQuery"
    @query-success="onQuerySuccess"
    @query-error="onQueryError"
  /> -->
  <h1>wat</h1>
</div>
</template>
<script>
import Vue from 'vue';

import { mapActions } from 'vuex';

const defaultQuery = `
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?c (MIN(?class) AS ?class) (COUNT(?x) AS ?count)
WHERE {
    ?x a ?c.
    ?c rdfs:label ?class.
}
GROUP BY ?c
ORDER BY DESC(?count)
`.trim()

export default Vue.component('bob-viz-sparql', {
  data: () => ({
    query: defaultQuery
  }),
  methods: {
    ...mapActions('bobViz', ['setResults', 'setQuery']),
    onQuerySuccess(results) {
      this.setResults(results)
    }
  },
  watch: {
    query(query) {
      this.setQuery(query)
    }
  }
})
</script>
