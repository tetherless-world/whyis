import Vue from 'vue'
import DataVoyagerPage from './data-voyager-page.vue'

Vue.component('data-voyager', () => import('./data-voyager.vue'))
Vue.component('data-voyager-page', DataVoyagerPage)
