<template>
    <div class="utility-roverflow">
        <div class="utility-content__result">
            <span class="utility-color" v-if="otherArgs != null && authenticated">Home > <strong>My Chart</strong> > </span>
            <span v-if="results.length == 1">Just {{results.length}} result (0.59 seconds)</span>
            <span v-else-if="results.length >= 2">About {{results.length}} results (0.59 seconds)</span>
            <span v-else>No result (0.59 seconds)</span>
        </div>
        <div class="viz-content">
            <md-card v-for="(result, index) in results" :key="index" @click.native.prevent="navigate(result)">
                <md-card-media-cover md-solid >
                    <md-card-media md-ratio="4:3">
                    <img :src="result.thumbnail" :alt="result.label">
                    </md-card-media>
                    <md-card-area class="utility-gridbg">
                        <md-card-header class="utility-show_hide">
                            <span class="md-subheading">
                                <strong>{{ result.label }}</strong>
                            </span>
                            <span class="md-body-1">{{ reduceDescription(result.description) }}</span>
                        </md-card-header>
                    </md-card-area>
                </md-card-media-cover>
            </md-card>
        </div>
        <pagination v-if="results.length >= 12" />
    </div>
</template>
<style scoped lang="scss" src="../static/css/main.scss"></style>
<script>
    import { eventCourier as ec, state } from '../store'
    import { router } from '../router/routes'
    import pagination from './Pagination'
    import { Loader } from '../js/index'
    import { getViewUrl } from '../../../../utilities/views'
    export default {
        name: "viz-grid",
        mixins: [router],
        props: ['globalargs', 'authenticated'],
        data() {
            return {
                results: [],
                loading: false,
                loadError: false,
                otherArgs: null
            }
        },
        components: {
            pagination
        },
        methods: {
            navigate(args) {
                // return window.location = `${window.location.origin}/about?uri=${args.identifier}`
                return this.changeRoute("single", args)
            },
            reduceDescription(args) {
                let arr, arrSplice
                arr = args.split(" ")
                arr.splice(15)
                arrSplice = arr.reduce((a,b) => `${a} ${b}`, "")
                return `${arrSplice}...`
            },
            loadVisualization () {
                this.loading = true;
                /** passing view=instances&uri=this.parsedArg */ 
                const pageUri = getViewUrl(this.globalargs, "instances")
                this.chart = Loader(pageUri)
            }
        },
        async beforeMount(){
            const reslt = await this.loadVisualization();
            if(reslt == false) {
                return this.loadError = true;
            }
        },
        created(){
            ec
            .getState()
            .$on("appstate", (data) => this.results = data)
            .$on("route-args", (data) => this.otherArgs = data)
        }
    }
</script>