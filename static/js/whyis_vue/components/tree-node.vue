<template>
  <li class="TreeNode">
    <md-progress-spinner :style="{'visibility':loading}" :md-diameter="20" :md-stroke="3" md-mode="indeterminate"></md-progress-spinner>
    <span>
      <span :class="['caret', expanded ? 'caret-down' : '']" 
            :style="noChildren ? 'visibility : hidden' : ''" 
            @click="noChildren ? '' : caretClicked()"> </span>
      <span v-if="(node.label && node.label != 'nan')"> 
            {{node.label}} -
      </span>
      <a :href="'#/'+node.label.replace(' ','')">{{node.class}}</a>
    </span>
    <ul v-if="childNodes && childNodes.length"  :class="['nested', expanded ? 'active' : '' ]">
      <TreeNode v-for="(child, index) in childNodes" :node="child" :key="'child'+index"></TreeNode>
    </ul>
  </li>
</template>

<script>
import axios from 'axios';
export default {
    name: "TreeNode",
    props: {
        node: Object
    },
    data: function() {
        return {
            expanded: false,
            childNodes: this.node.children,
            noChildren: false,
            loading: 'hidden',
        }
    },
    methods:{
        caretClicked(){
            if (!this.childNodes && this.node.class){
                this.loading = 'visible'
                this.getSubClasses()
                .then( results => {
                    if (!this.childNodes.length){
                        this.noChildren = true;
                    }
                    this.loading = 'hidden';
                } )
            }
            this.expanded = !this.expanded;
        },
        getSubClasses(){
            return axios.get(
                `${ROOT_URL}about?view=incoming&uri=${this.node.class}`)
            .then(response => {
                let incomingClasses = response.data.filter(resItem => resItem["link_label"].toLowerCase()=="sub class of")
                this.childNodes = incomingClasses.map(arrItem => {
                    return {
                        label: arrItem["source_label"],
                        class: arrItem["source"]
                    }
                })
            })
        }
    },
};
</script>


<style scoped lang="scss">
/* Remove default bullets */
ul, #topLevelTree {
  list-style-type: none;
}

/* Style the caret/arrow */
.caret {
  cursor: pointer;
  user-select: none; /* Prevent text selection */
  width: max-content;
  border: none;
  margin-bottom: 20px
}

/* Create the caret/arrow with a unicode, and style it */
.caret::before {
  content: "\25B6";
  color: black;
  display: inline-block;
  margin-right: 6px;
}

/* Rotate the caret/arrow icon when clicked on (using JavaScript) */
.caret-down::before {
  transform: rotate(90deg);
}

/* Hide the nested list */
.nested {
  display: none;
}

/* Show the nested list when the user clicks on the caret/arrow (with JavaScript) */
.active {
  display: block;
}
</style>