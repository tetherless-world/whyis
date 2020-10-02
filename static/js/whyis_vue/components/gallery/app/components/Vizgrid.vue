<template>
    <div class="">
        <spinner :loading="loading" text='Loading charts...' v-if="loading"/>
        <div class="utility-roverflow" v-else>
            <div class="utility-content__result">
                <!-- TODO TIME TO RESULT -->
                <span v-if="otherArgs == null && results.length <= 1">{{results.length}} result (0.59 seconds)</span>
                <span v-else-if="otherArgs == null && results.length >= 2">About {{results.length}} results (0.59 seconds)</span>
                <span class="utility-color" v-else-if="otherArgs != null">Home > <strong> {{ otherArgs }}</strong> > About {{results.length}} results (0.59 seconds)</span>
                <span v-else>No result (0.59 seconds)</span>
            </div>
            <div class="viz-content">
                <md-card v-for="(result, index) in newResults" :key="index" class="btn--animated">
                    <div class="utility-gridicon" v-if="authenticated && authenticated.admin=='True'">
                        <div @click.prevent="bookmark(result.name, true)" v-if="result.bookmark"><md-icon>bookmark</md-icon></div>
                        <div @click.prevent="bookmark(result.name, false)" v-else><md-icon>bookmark_border</md-icon></div>
                        <div @click.prevent="deleteChart(result)"><md-icon>delete_outline</md-icon></div>
                    </div>
                    <div class="utility-gridicon" v-else-if="authenticated">
                        <div @click.prevent="bookmark(result.name, true)" v-if="result.bookmark"><md-icon>bookmark</md-icon></div>
                        <div @click.prevent="bookmark(result.name, false)" v-else><md-icon>bookmark_border</md-icon></div>
                    </div>
                    <md-card-media-cover md-solid @click.native.prevent="navigate(result)">
                        <md-card-media md-ratio="4:3">
                        <img :src="result.backup.depiction" :alt="result.backup.title">
                        </md-card-media>
                        <md-card-area class="utility-gridbg">
                            <md-card-header class="utility-show_hide">
                                <span class="md-subheading">
                                    <strong>{{ result.backup.title }}</strong>
                                </span>
                                <span class="md-body-1">{{ reduceDescription(result.backup.description) }}</span>
                            </md-card-header>
                        </md-card-area>
                    </md-card-media-cover>
                </md-card>
            </div>
            <pagination v-if="results.length > basePage" :cpage="currentPage" :tpages="totalPages" />
        </div>
    </div>
</template>
<style scoped lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
    import EventServices from '../../../../modules/events/event-services'
    import pagination from './Pagination'
    export default {
        name: "viz-grid",
        props: ['authenticated'],
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
            navigate(args) {
                return window.location = args.backup.uri
            },
            reduceDescription(args) {
                let arr, arrSplice
                arr = args.split(" ")
                arr.splice(15)
                arrSplice = arr.reduce((a,b) => `${a} ${b}`, "")
                return `${arrSplice}...`
            },
            bookmark(args, exist){
                return EventServices.createChartBookMark(args, exist);
            },
            deleteChart(chart){
                return EventServices.$emit("dialoguebox", {status: true, delete: true, title: "Delete Chart", message: `Are you sure you want to delete this chart?`, chart})
            },
            async loadAllCharts(){
                this.loading = true
                await EventServices.fetchAllCharts()
                return this.loading = false
            }
        },
        beforeMount(){
            return this.loadAllCharts()
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