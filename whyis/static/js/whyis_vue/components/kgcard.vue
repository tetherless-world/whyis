<template>
  <div class="card btn--animated h-100" @click="navigate(entity)" style="cursor: pointer;">
    <div class="card-img-top-wrapper position-relative overflow-hidden">
      <img 
        :src="getViewUrl(entity.thumbnail)" 
        :alt="entity.label" 
        class="card-img-top" 
        style="aspect-ratio: 4/3; object-fit: cover;"
        v-if="entity.thumbnail"
      >
      <img 
        :src="$root.$data.root_url + 'static/images/rdf_flyer.svg'" 
        :alt="entity.label" 
        class="card-img-top"
        style="aspect-ratio: 4/3; object-fit: cover;"
        v-else
      >
      <div class="card-img-overlay d-flex align-items-end p-0">
        <div class="card-body bg-dark bg-opacity-75 text-white w-100 utility-gridbg utility-show_hide">
          <h5 class="card-title mb-1">
            <strong>{{ entity.label }}</strong>
          </h5>
          <p class="card-text small mb-0">{{ entity.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
    import { Slug } from '../modules'
    import { getViewUrl } from '../utilities/views'
    export default {
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
    }
</script>
