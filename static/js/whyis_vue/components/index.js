import './utils/spinner'
import './utils/dialog'
import './utils/range-slider'
import './pages'
import "./kg-card";
import "./search-autocomplete";
import "./table-view";
import './yasqe';
import './yasr';
import './gallery';
import './add-type';
import './add-attribute';
import './add-link';
import './add-knowledge-menu';
import './accordion'
import './bob-viz-modules'
import './facet-browser'
import './facets'

import Vue from 'vue';
Vue.component('vega-lite', () => import('./vega-lite-wrapper'))
Vue.component('data-voyager', () => import('./data-voyager'))
