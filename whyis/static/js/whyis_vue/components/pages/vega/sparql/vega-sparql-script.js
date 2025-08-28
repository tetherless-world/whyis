
import { EventServices } from '../../../../modules'

export default {
  name: 'vega-sparql-script.js',
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
}
