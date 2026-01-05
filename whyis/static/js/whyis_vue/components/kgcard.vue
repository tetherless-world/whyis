<template>
  <div class="card">
    <img :src="getViewUrl(entity.thumbnail)" class="card-img-top" :alt="entity.label" v-if="entity.thumbnail" style="height: 10em; object-fit: contain;">
    <img :src="$root.$data.root_url + 'static/images/rdf_flyer.svg'" class="card-img-top" :alt="entity.label" v-else style="height: 10em; object-fit: contain;">
    <div class="card-body">
      <h6 class="card-title" >{{ entity.label }}</h6>
      <p class="card-text flex-grow-1">{{ entity.description }}</p>
      <a :href="getViewUrl(entity.identifier, 'view')" class="card-link">View</a>
      <a :href="getViewUrl(entity.identifier, 'explore')" class="card-link">Explore</a>
    </div>
  </div>
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
