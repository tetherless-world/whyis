import Vue from 'vue';
import * as Fn from './functions';

const EventServices = new Vue({
    data:{
        chartListings: [],
        authUser: undefined,
        navOpen: false,
        tempChart: undefined,
        thirdPartyRestBackup: false,
        speedDials: false,
        filterExist: false,
        currentPage: 1,
        settingsPage: 1,
        vizOfTheDay: true,
    },
    watch:{
        chartListings(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
        },
        authUser(newVal){
            if(newVal){
                if(newVal.name){
                    this.getUserBkmk()
                }
                this.$emit('isauthenticated', this.authUser);
            }
        },
        vizOfTheDay(newValue){
            if(newValue){
                this.$emit('vizofdd', newValue)
            }
        }
    },
    methods: {...Fn.controller},
    created(){
        this.$on('vodd', data => this.vizOfTheDay = data);
        this.confirmConfig()
        return this.confirmAuth()
    }
})


/** Outside Navigation & DialogBox Click Handler */
document.addEventListener("click", () => {
    EventServices.$data.navOpen = false;
    EventServices.$emit('close-filter')
});

export default EventServices;