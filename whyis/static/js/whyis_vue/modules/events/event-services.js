import { reactive, watch } from 'vue';
import * as Fn from './functions';

// Simple event emitter for Vue 3
class EventEmitter {
    constructor() {
        this.events = {};
    }
    
    $on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return this; // for chaining
    }
    
    $emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }
    
    $off(event, callback) {
        if (this.events[event]) {
            if (callback) {
                this.events[event] = this.events[event].filter(cb => cb !== callback);
            } else {
                this.events[event] = [];
            }
        }
    }
}

// Create reactive data
const data = reactive({
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
});

// Create the event services object
const EventServices = Object.assign(new EventEmitter(), {
    // Add reactive data properties
    get chartListings() { return data.chartListings; },
    set chartListings(val) { data.chartListings = val; },
    get organization() { return data.organization; },
    set organization(val) { data.organization = val; },
    get author() { return data.author; },
    set author(val) { data.author = val; },
    get authUser() { return data.authUser; },
    set authUser(val) { data.authUser = val; },
    get navOpen() { return data.navOpen; },
    set navOpen(val) { data.navOpen = val; },
    get tempChart() { return data.tempChart; },
    set tempChart(val) { data.tempChart = val; },
    get thirdPartyRestBackup() { return data.thirdPartyRestBackup; },
    set thirdPartyRestBackup(val) { data.thirdPartyRestBackup = val; },
    get speedDials() { return data.speedDials; },
    set speedDials(val) { data.speedDials = val; },
    get filterExist() { return data.filterExist; },
    set filterExist(val) { data.filterExist = val; },
    get currentPage() { return data.currentPage; },
    set currentPage(val) { data.currentPage = val; },
    get settingsPage() { return data.settingsPage; },
    set settingsPage(val) { data.settingsPage = val; },
    
    // Add controller methods
    ...Fn.controller,
    
    // Initialize method (replaces created hook)
    init() {
        this.toggleVizOfTheDay()
        this.confirmConfig()
        return this.confirmAuth()
    }
});

// Set up watchers
watch(() => data.chartListings, (newVal, oldVal) => {
    if (newVal != oldVal) {
        EventServices.getState();
    }
});

watch(() => data.authUser, (newVal) => {
    if (newVal) {
        if (newVal.name) {
            EventServices.getUserBkmk()
        }
        EventServices.$emit('isauthenticated', EventServices.authUser);
    }
});

watch(() => data.organization, (newVal, oldVal) => {
    if (newVal != oldVal) {
        EventServices.getState();
    }
    EventServices.$emit('organizationSelected', EventServices.organization);
});

watch(() => data.author, (newVal, oldVal) => {
    if (newVal != oldVal) {
        EventServices.getState();
    }
    EventServices.$emit('authorSelected', EventServices.author);
});

// Initialize
EventServices.init();

/** Outside Navigation & DialogBox Click Handler */
document.addEventListener("click", () => {
    EventServices.navOpen = false;
    EventServices.$emit('close-filter')
});

export default EventServices;