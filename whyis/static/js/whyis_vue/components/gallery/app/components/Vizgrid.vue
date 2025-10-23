<template>
    <div class="">
        <spinner :loading="loading" text='Loading...' v-if="loading"/>
        <div class="utility-roverflow" v-else>
            <div class="utility-content__result">
                <!-- TODO TIME TO RESULT -->
                <span v-if="otherArgs == null && results.length <= 1">{{results.length}} result (0.59 seconds)</span>
                <span v-else-if="otherArgs == null && results.length >= 2">About {{results.length}} results (0.59 seconds)</span>
                <span class="utility-color" v-else-if="otherArgs != null">Home > <strong> {{ otherArgs }}</strong> > About {{results.length}} results (0.59 seconds)</span>
                <span v-else>No result (0.59 seconds)</span>
            </div>
            <div class="viz-content">
                <div v-for="(result, index) in newResults" :key="index" class="card btn--animated h-100">
                    <div class="utility-gridicon position-absolute top-0 end-0 p-2" style="z-index: 10;" v-if="authenticated && authenticated.admin=='True' && instanceType=='http://semanticscience.org/resource/Chart'">
                        <button class="btn btn-link p-1" @click.prevent="bookmark(result.name, true)" v-if="result.bookmark">
                            <i class="bi bi-bookmark-fill text-warning"></i>
                        </button>
                        <button class="btn btn-link p-1" @click.prevent="bookmark(result.name, false)" v-else>
                            <i class="bi bi-bookmark text-muted"></i>
                        </button>
                        <button class="btn btn-link p-1" @click.prevent="deleteChart(result)">
                            <i class="bi bi-trash text-danger"></i>
                        </button>
                    </div>
                    <div class="utility-gridicon position-absolute top-0 end-0 p-2" style="z-index: 10;" v-else-if="authenticated && instanceType=='http://semanticscience.org/resource/Chart'">
                        <button class="btn btn-link p-1" @click.prevent="bookmark(result.name, true)" v-if="result.bookmark">
                            <i class="bi bi-bookmark-fill text-warning"></i>
                        </button>
                        <button class="btn btn-link p-1" @click.prevent="bookmark(result.name, false)" v-else>
                            <i class="bi bi-bookmark text-muted"></i>
                        </button>
                    </div>
                    
                    <div class="card-img-top position-relative" @click.prevent="navigate(result)" style="cursor: pointer;">
                        <img :src="getViewUrl(result.thumbnail)" class="card-img-top" :alt="result.label" v-if="result.thumbnail" style="height: 200px; object-fit: cover;">
                        <img :src="$root.$data.root_url + 'static/images/rdf_flyer.svg'" class="card-img-top" :alt="result.label" v-else style="height: 200px; object-fit: cover;">
                        <div class="card-img-overlay d-flex align-items-end utility-gridbg">
                            <div class="card-header-content utility-show_hide w-100">
                                <h6 class="card-title text-white fw-bold mb-1">{{ result.label }}</h6>
                                <p class="card-text text-white-50 small mb-0">{{ reduceDescription(result.description) }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <pagination v-if="results.length > basePage" :cpage="currentPage" :tpages="totalPages" />
        </div>
    </div>
</template>
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
    import { EventServices, Slug } from '../../../../modules'
    import { getViewUrl } from '../../../../utilities/views'
    import pagination from './Pagination.vue'
    import axios from 'axios'
    export default {
        name: "viz-grid",
        props:{
          authenticated: {
            type: Boolean,
            require: true
          },
          instancetype: {
            type: String,
            require: true
          }
        },
        data() {
            return {
                results: [],
                newResults: [],
                loading: false,
                loadError: false,
                otherArgs: null,
                totalPages: 1,
                currentPage: 1,
                basePage: 10,
                perPage: 10,
            }
        },
        watch: {
            results(newValues, oldValues){
                if(newValues && newValues != oldValues){
                    const length = newValues.length;
                    let tpages = Math.round(length/this.basePage)
                    if(length <= this.basePage){
                       this.totalPages = 1;
                    } else if(length%this.basePage == 0){
                        this.totalPages = tpages;
                    } else if(length%this.basePage <= 4) {
                        this.totalPages = tpages + 1;
                    } else {
                        this.totalPages = tpages;
                    }
                }
                this.showResults()
            },
            currentPage(newValues, oldValues){
                if(newValues != oldValues){
                    this.showResults()
                }
            }
        },
        components: {
            pagination
        },
        methods: {
            async showResults(){
                this.perPage = this.currentPage * this.basePage
                const newArr = [];
                await this.results.map((e,i) => {
                    if(i+1 <= this.perPage && i+1 > this.perPage - this.basePage){
                        newArr.push(e)
                    }
                })
                return this.newResults = newArr;
            },
            getViewUrl(uri, view) { return getViewUrl(uri, view) },
            navigate(args) {
                return window.location = getViewUrl(args.identifier,"view")
            },
            reduceDescription(args) {
                let arr, arrSplice, res
                arr = args.split(" ")
                arr.splice(15)
                arrSplice = arr.reduce((a,b) => `${a} ${b}`, "")
                res = Slug(arrSplice)
                return `${res}...`
            },
            bookmark(args, exist){
                return EventServices.createChartBookMark(args, exist);
            },
            deleteChart(chart){
                return EventServices.$emit("dialoguebox", {status: true, delete: true, title: "Delete", message: `Are you sure you want to delete this chart?`, chart})
            },

        },
        async mounted (){
            this.loading = true
            // Commenting out VOTD until we can figure out how to do it generically.
            //const vvodd = false // await EventServices.getVizOfTheDayStatus()
            //const result = await EventServices.fetchInstances(this.type)
            const result = await axios.get(`${ROOT_URL}about`,
                                           { params: {
                                               view: "instances",
                                               uri: this.instancetype
                                             }
                                           })
            this.results = result.data
            //if(result.length > 0 && vvodd.status == true){
            //    let viz = result[0];
            //    if("backup" in viz){
            //        this.loading = false
            //        // return window.location = viz.backup.uri
            //    }
            //}
            this.loading = false
        },
        created(){
            EventServices
            .$on("appstate", (data) => {
                this.results = data.filter((el) => el.enabled == true)
            })
            .$on("filterexistcancel", (data) => this.results = data)
            .$on("filterexist", (data) => this.results = data)
            .$on("chartpagination", (data) => this.currentPage = data)
        }
    }
</script>