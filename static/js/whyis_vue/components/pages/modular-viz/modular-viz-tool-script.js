import Vue from 'vue';
import splitPane from 'vue-splitpane';


export default Vue.component('modular-viz-tool', {
  data() {
    return {
      sparqlQuery: "",
      sparqlError: false,
      jsonResults: {},
    }
  },
  methods: {
    passData(){
      return
    },
    convertSparqlToJson(){
      return
    },
    async getSparqlData () {
      try {
        const results = await querySparql(this.sparqlQuery)
        this.onQuerySuccess(results)
      } catch (error) {
        this.onQueryError(error)
      }
    },
    onQuerySuccess (results) {
      this.sparqlError = false
      this.jsonResults = results
      console.log(results)
    },
    onQueryError (error) {
      this.sparqlError = true
      console.warn('SPARQL QUERY ERROR\n', error)
    },
    isSparqlError() {
      return this.sparqlError
    },
    onSpecJsonError () {
      console.log('bad', arguments)
    },
  },
  components: {
    splitPane
  },
  created() { 
    
  }
})