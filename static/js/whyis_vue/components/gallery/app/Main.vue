<template>
  <div class="utility-bg">
    <component v-bind:is="route" :passedargs="routeArgs" :globalargs="instances"></component>
  </div>
</template>
<style scoped lang="scss" src="./static/css/main.scss"></style>
<script>
  import Vue from 'vue'
  import { router } from './router/routes'
  import { eventCourier as ec } from './store'
  import home from './components/HomePage.vue'
  import single from './components/Single.vue'
  export default Vue.component('viz-gallery', {
    mixins: [router],
    props: ["instances"],
    data(){
      return {
        route: null,
        routeArgs: null
      }
    },
    components: {
      /** The app have two component page. Append new component pages here!!! */
      home,
      single    
    },
    beforeMount() {
      return this.changeRoute('home');
    },
    created() {
      /** Used this for managing routes internally - Ignore if not needed!!! */
      ec
        .$on('route-changed', (data) => {
          return this.route = data;
        })
        .$on('route-args', (data) => {
          return this.routeArgs = data;
        })
    },
  })
</script>


