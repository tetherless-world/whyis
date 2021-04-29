import './utils/spinner'
import './utils/dialog'
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

import Vue from 'vue';
Vue.component('vega-lite', () => import('./vega-lite-wrapper'))
