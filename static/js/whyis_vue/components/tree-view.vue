<template>
<div>
    <ul>
        <tree-node v-for="(data, index) in rootNodes" :key="'topLevel'+index" :node="data"></tree-node>
    </ul>
</div>
</template>

<script>
import Vue from "vue";
import axios from 'axios';
import TreeNode from "./tree-node"

export default Vue.component('tree-view', {
    props: {
        entity_uri: String,
        root_node_type: {
            type: String,
            default: 'toplevel'
        },
    },
    components: {
        TreeNode,
    },
    data: function() {
        return {
            rootNodes: [],
        };
    },
    created: function() {
        let topLevel = axios.get(
            `${ROOT_URL}about?view=${this.root_node_type}&uri=${this.entity_uri}`)
            .then(response => {
                this.rootNodes = response.data
            })
    },
});
</script>

<style scoped lang="scss">
/* Remove default bullets from top level */
ul, #topLevelTree {
  list-style-type: none;
}
</style>