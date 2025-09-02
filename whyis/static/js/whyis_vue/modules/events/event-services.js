/**
 * Central event management service for the Whyis Vue application.
 * Provides a reactive event bus for managing application state and user interactions.
 * 
 * @module event-services
 */

import Vue from 'vue';
import * as Fn from './functions';

/**
 * Global event service instance for managing application-wide state and events.
 * Uses Vue's reactivity system to provide real-time updates across components.
 * 
 * @type {Vue}
 * @property {Array} chartListings - List of available chart visualizations
 * @property {Object|undefined} organization - Currently selected organization
 * @property {Object|undefined} author - Currently selected author
 * @property {Object|undefined} authUser - Authenticated user information
 * @property {boolean} navOpen - Navigation menu open/closed state
 * @property {Object|undefined} tempChart - Temporary chart data during editing
 * @property {boolean} thirdPartyRestBackup - Third-party backup service status
 * @property {boolean} speedDials - Speed dial controls enabled/disabled
 * @property {boolean} filterExist - Filter panel visibility state
 * @property {number} currentPage - Current pagination page number
 * @property {number} settingsPage - Settings panel page number
 */
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
        /**
         * Watches for changes in chart listings and updates application state
         * @param {Array} newVal - New chart listings array
         * @param {Array} oldVal - Previous chart listings array
         */
        chartListings(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
        },
        
        /**
         * Watches for authentication changes and emits events
         * @param {Object} newVal - New authenticated user object
         */
        authUser(newVal){
            if(newVal){
                if(newVal.name){
                    this.getUserBkmk()
                }
                this.$emit('isauthenticated', this.authUser);
            }
        },
        
        /**
         * Watches for organization selection changes
         * @param {Object} newVal - New organization object
         * @param {Object} oldVal - Previous organization object
         */
        organization(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
            this.$emit('organizationSelected', this.organization); 
        },
        
        /**
         * Watches for author selection changes
         * @param {Object} newVal - New author object
         * @param {Object} oldVal - Previous author object
         */
        author(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
            this.$emit('authorSelected', this.author); 
        }
    },
    methods: {...Fn.controller},
    
    /**
     * Initializes the event service when the Vue instance is created
     */
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