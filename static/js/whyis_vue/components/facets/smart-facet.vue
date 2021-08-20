<template>
<div> 
    <label>{{facetobject.label}}</label>
    <div>
        <span v-for="(chip, index) in selected" 
                v-bind:key="index + 'chip'" 
                style="padding: 4px;">
            <md-chip md-deletable @md-delete="deletechip(index)">{{selected[index].name}}</md-chip>
        </span>
        <md-autocomplete flex
            :value="selectedItem"
            md-min-length="0"
            md-input-placeholder="+"
            :md-options="facetobject.values"
            @md-selected="selectedItemChange"
            @md-opened="processAutocompleteMenu"
            @md-closed="processAutocompleteMenu(true)">

            <template style="width: 90% !important; left: 1px !important; max-width: 90% !important" slot="md-autocomplete-item" slot-scope="{ item, term }">
                <md-highlight-text :md-term="term">{{ item.name }} {{item.unit_label ? ("(" + item.unit_label + ")") : ""}}</md-highlight-text>
                <!-- <span md-highlight-text="vm.facet.searchText" md-highlight-flags="^i">{{ item.name }} {{item.unit_label ? ("(" + item.unit_label + ")") : ""}}</span> -->
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
        selectedItemChange(item){
            this.selected.push(item);
            this.$emit('selected-facets-changed', {facet: this.facetobject.facetId, facetvalues: this.selected});
            this.selectedItem = "";
        },
        deletechip(index){
            if (index > -1) {
                this.selected.splice(index, 1);
            }
            this.$emit('selected-facets-changed', {facet: this.facetobject.facetId, facetvalues: this.selected});
            return this.selected;
        },
        // Formats the dropdown menu. Runs only while the menu is open
        processAutocompleteMenu (param) {
            const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
            if(itemListContainer.length >= 1) {
                itemListContainer[0].style['z-index'] = 12;
                itemListContainer[0].style['width'] = "90%"
                itemListContainer[0].style['max-width'] = ""
                return status = true
            }
        },
    },
});
</script>