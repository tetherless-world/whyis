<template>
  <li class="TreeNode">
    <span :class="['caret', expanded ? 'caret-down' : '']" @click="caretClicked()">
        {{ (node.label && node.label != 'nan') ? node.label+' ('+node.class+')' : node.class }}
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
        }
    },
    methods:{
        caretClicked(){
            this.expanded = !this.expanded;
            if (!this.childNodes && this.node.class){
                this.getSubClasses()
            }
        },
        getSubClasses(){
            axios.get(
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