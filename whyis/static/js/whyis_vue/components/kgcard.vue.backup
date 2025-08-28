<template>
  <md-card class="btn--animated">
      <md-card-media-cover md-solid @click.native.prevent="navigate(entity) " >
          <md-card-media md-ratio="4:3" >
          <img :src="getViewUrl(entity.thumbnail)" :alt="entity.label" v-if="entity.thumbnail">
          <img :src="$root.$data.root_url + 'static/images/rdf_flyer.svg'" :alt="entity.label" v-else>
          </md-card-media>
          <md-card-area class="utility-gridbg">
              <md-card-header class="utility-show_hide">
                  <span class="md-subheading">
                      <strong>{{ entity.label }}</strong>
                  </span>
                  <span class="md-body-1">{{ entity.description }}</span>
              </md-card-header>
          </md-card-area>
      </md-card-media-cover>
  </md-card>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
    import Vue from "vue";
    import { Slug } from '../modules'
    import { getViewUrl } from '../utilities/views'
    export default Vue.component('kgcard', {
        name: "kgcard",
        props:{
          entity: {
            require: true
          },
        },
        data() {
            return {
            }
        },
        methods: {
            getViewUrl(uri, view) { return getViewUrl(uri, view) },
            navigate(entity) {
                return window.location = getViewUrl(entity.identifier,"view")
            },
            reduceDescription(args) {
                if (args == null) return args
                let arr, arrSplice, res
                arr = args.split(" ")
                arr.splice(15)
                arrSplice = arr.reduce((a,b) => `${a} ${b}`, "")
                res = Slug(arrSplice)
                return `${res}...`
            },

        },
    })
</script>
