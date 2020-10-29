import Vue from 'vue';
import * as Fn from './functions';

const EventServices = new Vue({
    data:{
        chartListings: [],
        // institutions: ["Duke University", "California Institute of Technology", "Northwestern University", "Rensselaer Polytechnic Institute", "University of Vermont"],
        // authors: ["Author 1", "Author 2", "Other Author", "Research Intern"],
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
        // institutions(newVal, oldVal){
        //     if(newVal != oldVal){
        //         this.getState();
        //     }
        //     this.$emit('institutionsupdated', this.institutions);
        // },
        // authors(newVal, oldVal){
        //     if(newVal != oldVal){
        //         this.getState();
        //     }
        //     this.$emit('authorsupdated', this.authors);
        // },
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