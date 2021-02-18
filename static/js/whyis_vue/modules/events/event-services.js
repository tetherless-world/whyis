import Vue from 'vue';
import * as Fn from './functions';

const EventServices = new Vue({
    data:{
        chartListings: [],
        organization: undefined,
        author: undefined,
        authUser: undefined,
        navOpen: false,
        tempChart: undefined,
        thirdPartyRestBackup: false,
        speedDials: false,
        filterExist: false,
        currentPage: 1,
        settingsPage: 1,
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
        organization(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
            this.$emit('organizationSelected', this.organization); 
        },
        author(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
            this.$emit('authorSelected', this.author); 
        }
    },
    methods: {...Fn.controller},
    created(){
        this.toggleVizOfTheDay()
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