<template>
  <div class="card btn--animated h-100">
    <div class="card-img-top position-relative" @click.prevent="navigate(entity)" style="cursor: pointer;">
      <img :src="getViewUrl(entity.thumbnail)" class="card-img-top" :alt="entity.label" v-if="entity.thumbnail" style="height: 200px; object-fit: cover;">
      <img :src="$root.$data.root_url + 'static/images/rdf_flyer.svg'" class="card-img-top" :alt="entity.label" v-else style="height: 200px; object-fit: cover;">
      <div class="card-img-overlay d-flex align-items-end utility-gridbg">
        <div class="card-header-content utility-show_hide w-100">
          <h6 class="card-title text-white fw-bold mb-1">{{ entity.label }}</h6>
          <p class="card-text text-white-50 small mb-0">{{ entity.description }}</p>
        </div>
      </div>
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
