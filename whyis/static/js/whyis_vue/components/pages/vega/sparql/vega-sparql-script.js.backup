import Vue from 'vue'
import { EventServices } from '../../../../modules'

export default Vue.component('vega-sparql', {
  data() {
    return {
      loading: false,
    }
  },
  mounted(){
    var yasgui = YASGUI(document.getElementById("yasgui"), {
      yasqe:{
        sparql:{
          endpoint:'{{endpoint}}',
          requestMethod: "POST"
        }
      },
      yasr : {
        table : {
          fetchTitlesFromPrefLabel : false
        }
      }
    });
  },
  created () {
    if(EventServices.authUser == undefined){
      return EventServices.navTo('view', true)
    }
  }
})
