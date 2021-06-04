<template>
<div> 
    <label>{{facetobject.label}}</label>
    <div>
        <span v-for="(chip, index) in selected" 
                v-bind:key="index + 'chip'" 
                style="padding: 4px;">
            <md-chip md-deletable @md-delete="deletechip(index)">{{selected[index]}}</md-chip>
        </span>
        <md-autocomplete flex
            v-model="selectedItem"
            md-search-text="searchText"
            md-min-length="0"
            md-input-placeholder="+"
            :md-options="search()"
            @md-changed="resolveEntity"
            @md-selected="selectedItemChange">

            <template slot="md-autocomplete-item" slot-scope="{ item, term }">
                <md-highlight-text :md-term="term">{{ item }}</md-highlight-text>
                <span md-highlight-text="vm.facet.searchText" md-highlight-flags="^i">{{ item.name }} {{item.unit_label ? ("(" + item.unit_label + ")") : ""}}</span>
            </template>
        </md-autocomplete>
    </div>
</div>
</template>
<style scoped lang="scss" src="../../assets/css/main.scss"></style>
<script>
import Vue from "vue";

export default Vue.component('smart-facet', {
    props: ['facetobject'],
    data: function() {
        return {
            selected:[],
            selectedItem: null,
            searchText: "",

        };
    },
    methods: {
        //(item in search(vm.facet.searchText, vm.facet.getState() | orderBy:'-count')"
        search(){
            return this.facetobject.values
        },
        changed(){

        },
        selectedItemChange(){
            this.selected.push(this.selectedItem);
            console.log(this.selected)
        },
        resolveEntity(){

        },
        deletechip(index){
            if (index > -1) {
                this.selected.splice(index, 1);
            }
            return this.selected;
        },
    }
});
</script>