import Vue from 'vue'
import DataVoyagerPage from './data-voyager-page'

Vue.component('data-voyager', () => import('./data-voyager'))
Vue.component('data-voyager-page', DataVoyagerPage)
