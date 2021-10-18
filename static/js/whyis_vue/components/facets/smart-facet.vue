<template>
<div> 
    <div class="md-layout md-gutter"
            :class="`md-alignment-center-left`">
        <label class="md-layout-item" style="max-width:fit-content" >{{facetobject.label}}</label>
        <div class="md-layout-item" >
        <span  v-for="(chip, index) in selected" 
            v-bind:key="index + 'chip'" 
            style="padding: 4px;">
            <md-chip md-deletable @md-delete="deletechip(index)">{{selected[index].name}}</md-chip>
        </span>
        </div>
    </div>

    <md-autocomplete flex
        :value="selectedItem"
        md-min-length="0"
        md-input-placeholder="+"
        :md-options="facetobject.values"
        @md-selected="selectedItemChange"
        @md-opened="processAutocompleteMenu"
        @md-closed="processAutocompleteMenu(true)"
        style="width:90%">
        <template style="width: 90% !important; left: 1px !important; max-width: 90% !important" slot="md-autocomplete-item" slot-scope="{ item, term }">
            <md-highlight-text :md-term="term">{{ item.name }} {{item.unit_label ? ("(" + item.unit_label + ")") : ""}}</md-highlight-text>
        </template>
    </md-autocomplete>

    <div v-for="(facetName, index) in selected"
        v-bind:key="index + 'facetName'"
        style="padding: 20px;">
        <div v-if="selected[index].type=='quantitative'"  
        class="md-layout" 
        :class="`md-alignment-center-center`">
            <div class="md-layout-item">
                {{selected[index].name}}
            </div>
            <range-slider
                class="md-layout-item" 
                v-bind:rangeMin="facetName.min_value" 
                v-bind:rangeMax="facetName.max_value" 
                v-bind:externalMin="facetName.minValue ? facetName.minValue : facetName.min_value"
                v-bind:externalMax="facetName.maxValue ? facetName.maxValue : facetName.max_value"
                @minInput="facetName.minValue = $event"
                @maxInput="facetName.maxValue = $event"/>
            <div class="md-layout-item"></div>
        </div>
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
            var clone = JSON.parse(JSON.stringify(item));
            this.selected.push(clone);
            this.$emit('selected-facets-changed', {facet: this.facetobject.facetId, facetvalues: this.selected});
            this.selectedItem = "";
        },
        deletechip(index){
            if (index > -1) {
                if(this.selected[index].minValue) {
                    this.selected[index].minValue = null;                    
                }
                if(this.selected[index].maxValue) {
                    this.selected[index].maxValue = null;                    
                }
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