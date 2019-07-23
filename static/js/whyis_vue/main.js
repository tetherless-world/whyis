import Vue from 'vue'
import * as VueMaterial from "vue-material";
import "components/kg-card";

Vue.use(VueMaterial.default);

new Vue({
    el: '#page',
    data: {
        attributes:  ATTRIBUTES,
        uri: NODE_URI,
        description: DESCRIPTION,
        user: USER,
        node: NODE,
        root_url: ROOT_URL,
        base_rate: BASE_RATE,
        lod_prefix: LOD_PREFIX,
    }
});

