/**
 * The functions below are used by the event services module
 * 1. "confirmAuth": Checks if user is authenticated
 * 2. "toggleNav": Used for drawer nav toggling
 * 3. "confirmConfig": Parse third part rest config to WHYIS
 * 4. "navTo": Recieve an argument and return to specified location
 * 5. "checkRestValid": Initial Validation of restful config
 * 6. "checkIfRestValidate": Validate user, and rest config before sending req to REST
 * 7. "restCallFn": This function sends all req to REST
 * current_user.has_role('Admin')
 */


import { getViewUrl } from '../../utilities/views';
import { getCharts } from '../../utilities/vega-chart';

/** NEEDED FOR NANOMINE */
const LOCAL_DEV_SERVER = 'http://localhost:8000/nmr/chart';
const SERVER = `${window.location.origin}/nmr/chart`;
const URL = SERVER;

const controller = {
  confirmAuth(){
    if(Object.keys(USER).length){
      this.authUser = {...USER, user: this.getCurrentUserURI(USER.uri)};
      this.$emit('snacks', {status: true});
      return this.$emit('isauthenticated', this.authUser);
    }
  },

  toggleNav() {
    this.navOpen = !this.navOpen;
    return this.$emit('togglenavigation', this.navOpen);
  },

  confirmConfig(){
    const { mongoBackup, speedDialIcon } = CONFIGS;
    this.thirdPartyRestBackup = mongoBackup == "True" ? true : false;
    this.speedDials = speedDialIcon == "True" ? true : false;
    console.log('configs:', this.thirdPartyRestBackup, this.speedDials)
  },

  navTo(args, uri){
    if(uri){
      return window.location = `${window.location.origin}/about?view=${args}&uri=http:%2F%2Fsemanticscience.org%2Fresource%2FChart`;
    }
    return window.location=args
  },

  checkRestValid(){
    if(!this.thirdPartyRestBackup) {
      console.log('failed third party check')
      return false
    }
    console.log('passed third party check')
    return true
  },

  checkIfRestValidate(){
    if(!this.authUser){
      const err = new Error('User Authorization Failed!')
      throw err;
    }
    console.log('passed auth user')
    return this.checkRestValid()
  },

  async restCallFn(formData, URL, METHOD){
    const forms = formData ? {...formData} : undefined
    try {
      let result = await fetch(URL, {
        method: METHOD,
        headers: {
          Accept: '*/*',
          'Content-Type': 'application/json',
          // Authorization: 'Bearer' + cookies
        },
        body: JSON.stringify(forms)
      })
      if(result.status == 201) {
        result = await result.json()
        console.log(result)
        return result
      }
      console.log('returned rest but status not equal 201')
      return undefined
    } catch(err){
      throw err;
    }
  },

  async loadVisualization (args) {
    /** passing view=instances&uri=this.parsedArg */ 
    let data, processedData, uri;
    uri = NODE_URI
    const pageUri = getViewUrl(args, "instances")
    data = await fetch(pageUri, {
      method: "POST"
    });
    processedData = await data.json();
    return processedData;
  },

  async loadCharts(){
    let result;
    result = await getCharts()
    if(result.length){
      result = result.map((el) => {
        el.backup = el
        return el
      })
      return this.chartListings = result
    }
  },

  async fetchAllCharts(){
    if(!this.thirdPartyRestBackup) {
      return this.loadCharts()
    }
    const existingBookmark = await JSON.parse(localStorage.getItem('chartbkmk'));
    let result = await this.restCallFn(undefined, `${URL}/retrievecharts`, 'GET');
    if(result) {
      result = result.charts.map((el) => {
        el.backup = JSON.parse(el.backup)
        return el
      })
      if(!this.filterExist){
        if(!existingBookmark){
          return this.chartListings = result;
        } else {
          const filter = await result.filter(function(o1){
            return existingBookmark.some(function(o2){
              if(o2 && o2.chart){
                return o1.name === o2.chart.name;          
              }
            });
          })
          await filter.forEach(el => {
            el.bookmark = true;
          })
          return this.chartListings = result;
        }
      }
    }
  },

  async createBackUp(args, prevID, enabled, tags){
    console.log('enter create backup')
    if(this.checkIfRestValidate()){
      const uri = args && args.uri ? args.uri.split("/"): null;
      const name = uri != null ? uri[uri.length - 1] : null;
      const prevChartID = !prevID ? 'null' : prevID;
      const eStatus = !enabled ? false : true;
      const restored = !prevID ? false : true;
      const formData = {name: name, chart: args, creator: this.authUser.user, prevChartID: prevChartID, tag:tags, enabled:eStatus, restored:restored}
      console.log('formData:', formData)
      return this.restCallFn(formData, `${URL}/postcharts`, 'POST')
    }
    console.log('failed rest validate....')
  },

  async deleteAChart(chart) {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({name: chart._id, creator: this.authUser.user}, `${URL}/deletecharts`, 'DELETE')
      if(result){
        this.chartListings.find((el, index) => {
          if(el == chart){
            this.chartListings.splice(index, 1)
          }
        })
        return listNanopubs(chart.backup.uri)
          .then(nanopubs => nanopubs.map(nanopub => deleteNanopub(nanopub.np)))
          .then(() => {
            this.getState();
            return this.$emit('snacks', {status:true, message: "Chart Deleted Successfully!"})
          })
          .catch(err => {
            throw err
          })
      }
    }
  },

  async resetChart() {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({creator: this.authUser.user}, `${URL}/resetcharts`, 'POST')
      if(result){
        await this.fetchAllCharts();
        return this.$emit('snacks', {status:true, message: 'Chart Reset Completed'});
      }
      return this.$emit('snacks', {status:true, message: err, tip: "Try Again"});
    }
  },

  async getUserBkmk (){
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({creator: this.authUser.user}, `${URL}/retrievechartbkmks`, 'POST')
      if(result){
        if(result.charts.length > 0){
          localStorage.setItem('chartbkmk', JSON.stringify(result.charts));
        }
        return this.fetchAllCharts();
      }
      return this.$emit('snacks', {status:true, message: 'Error retreiving bookmarks', tip: "Refresh App"});
    }
  },

  async createChartBookMark(args, exist) {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({bkmk:args, status:exist, creator: this.authUser.user}, `${URL}/postchartbkmks`, 'POST')
      if(result){
        localStorage.removeItem('chartbkmk');
        this.getUserBkmk()
        return this.$emit('savedbookmark', {status:true, message: exist ? "Bookmark Removed!": "Bookmark Saved!"});
      }
      return this.$emit('savedbookmark', {status:true, message: 'Bookmark Error!', tip: "Try Again"});
    }
  },

  async filterChart(key, args, user) {
    let filter = [];
    if(!user) {
      this.chartListings.map((el) => {
        if(el.backup[key] == args){
          filter.push(el)
        }
      })
    } else {
      this.chartListings.map((el) => {
        if(el[key] == usermail){
          filter.push(el)
        }
      })
    }
    this.filterExist = true;
    return this.$emit('filterexist', filter);
  },

  cancelChartFilter(){
    this.filterExist = false;
    return this.$emit('filterexistcancel', this.chartListings)
  },

  getState(){
    return this.$emit('appstate', this.chartListings);
  },

  async tipController(arg) {
    const checkIntroStatus = await JSON.parse(localStorage.getItem('introstatus'));
    if(arg){
      return this.$emit("dialoguebox", {status: true, intro: true})
    }

    if(!checkIntroStatus){
      localStorage.setItem('introstatus', JSON.stringify(true));
      return this.$emit("dialoguebox", {status: true, intro: true});
    }
  },

  checkIfEditable(args){
    if(this.checkIfRestValidate()){
      /** TODO: Filter chartlistings and check if user/admin */
      if(args){
        const user = !this.authUser.user ? null : this.authUser.user
        const uri = args.split("/");
        const name = uri[uri.length - 1];
        this.chartListings.filter(el => {
          if(el.name == name && el.creator == user){
            this.$emit("allowChartEdit", true)
          }
        })
      }
    }
  },

  getCurrentUserURI(args){
    if(this.checkRestValid()){
      if(args){
        console.log('args', args)
        let user = args.split("/");
        user = !user[user.length - 1] ? args : user[user.length - 1];
        user = user == 'whyis' ? 'testuser' : user;
        console.log(user)
        return user
      }
    } else {
      console.log('failed to split user')
      return args
    }
  }
}

export {
  controller
}