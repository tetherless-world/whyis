<template>
    <div class="">
        <spinner :loading="loading" text='Loading...' v-if="loading"/>
        <div v-else>
            <div class="album">
                <kgcard v-for="(entity, index) in results" :key="index" :entity="entity"/>
            </div>
        </div>
    </div>
</template>
<style scoped lang="scss" >
.album {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(30rem, 1fr));
  grid-gap: 1rem;
  margin: 5rem auto;
  padding: 0 5rem;
}
</style>
<script>
    import Vue from "vue";
    import axios from 'axios'
    export default Vue.component('album', {
        name: "album",
        props:{
          instancetype: {
            type: String,
            require: true
          }
        },
        data() {
            return {
                results: [],
                loading: false,
                loadError: false,
                otherArgs: null,
                pageSize: 24,
            }
        },
        watch: {
        },
        components: {
        },
        methods: {
            async loadPage() {
                // non-page sized results means we've reached the end.
                if (this.results.length % this.pageSize > 0)
                    return
                const result = await axios.get(`${ROOT_URL}about`,
                                               { params: {
                                                   view: "instances",
                                                   uri: this.instancetype,
                                                   limit: this.pageSize,
                                                   offset: this.results.length
                                                 }
                                               })
                this.results.push(...result.data)
            },
            async scrollBottom () {
                if (Math.ceil(window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
                    await this.loadPage()
                }
            }
        },
        async mounted (){
            window.addEventListener("scroll", this.scrollBottom)
            this.loading = true
            await this.loadPage()
            this.loading = false
        },
        async unmounted() {
            window.removeEventListener("scroll", this.scrollBottom)
        },
        created(){
        }
    })
</script>
