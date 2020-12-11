<template>
<div>
    <slot>
        <!--Default button -->
        <button id="addtypebutton" class="md-button-icon"
            style="border:none">
            <i>+ Add type(s)</i>
        <md-tooltip>Specify additional type, subclass, or superclass</md-tooltip>
        </button>
    </slot>
    
    <div>
    <md-dialog :md-active.sync="active" style="margin-top: -4rem" :md-click-outside-to-close="true">
        <div class="utility-dialog-box_header" >
            <md-dialog-title> Specify additional types/classes</md-dialog-title>
        </div>
        <div style="margin:20px;">
            <md-autocomplete
                :value="selectedType" 
                :md-options="typeList" 
                :md-open-on-focus="true" 
                @md-changed="resolveEntityType"
                v-on:md-selected="selectedTypeChange"
                @md-opened="showSuggestedTypes"
            >
                <!-- @md-opened="setListStyle" -->
                <!-- @md-closed="setListStyle(true)" -->
            <!-- >  -->
                <label>Search for types</label>

                <template style="width: 90% !important; left: 1px !important;" slot="md-autocomplete-item" slot-scope="{ item }">
                <label style="white-space: pre-wrap" md-term="term" md-fuzzy-search="true">{{item.label}}</label>
                </template>
            
                <template style="width: 90% !important; left: 1px !important" slot="md-autocomplete-empty" slot-scope="{ term }">
                <p>No types or classes matching "{{ term }}" were found.</p>
                </template>
            </md-autocomplete>
            <div
                v-for="(chip, key) in typeChips" 
                v-bind:key="key + 'chips'">
                <md-chip v-model=typeChips[key] style="margin-bottom:4px">
                    {{typeChips[key].label}}
                    <button @click="removeChip(key)" style="border:none; border-radius:50%; margin-left:4px">x</button>
                </md-chip>
            </div>
        
            <div class="utility-margin-big viz-2-col">
                <div class="utility-align--right utility-margin-top"> 
                </div>
                <div class="utility-align--right utility-margin-top">
                <a @click.prevent="onCancel" class="btn-text btn-text--default"> &larr; Exit</a> &nbsp; &nbsp;
                <a @click.prevent="onSubmit" class="btn-text btn-text--default">Submit &rarr; </a>
                </div>
            </div>
        </div>
    </md-dialog>
    </div>
</div>
</template>
<style scoped lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import {getTypeList, getSuggestedTypes} from "../utilities/autocomplete-menu";
import { processFloatList, resetProcessFloatList } from '../utilities/dialog-box-adjust';
import { postNewNanopub } from '../utilities/nanopub'

export default Vue.component('add-type', {
    props: ['attributes'],
    data: function() {
        return {
            id: null,
            typeList: [],
            selectedType: null,
            typeChips: [],
            status: false,
            active: false,
        };
    },
    methods: {
        async showSuggestedTypes(){
            this.typeList = await getSuggestedTypes(this.attributes);
        },
        async resolveEntityType(query){
            this.typeList = await getTypeList(query);
        },
        selectedTypeChange(item){
            this.typeChips.push(item);
        },
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
            return processFloatList()
        },
        removeChip(index){
            this.typeChips.splice(index, 1);
        },
        resetDialogBox(){
            this.active = !this.active;
            this.typeChips = []
            return resetProcessFloatList();
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.saveNewTypes();
            return this.resetDialogBox();
        },
        async saveNewTypes () {
            let deletePromise = Promise.resolve()
            const uri = this.attributes;
            const types = this.processTypeChips();
            const jsonLd = {
                '@id': this.attributes,
                '@type': types, 
            }
            await deletePromise
            try{
                return postNewNanopub(jsonLd)
            } catch(err){
                return alert(err)
            }
        },
        processTypeChips () {
            var processedChips = this.typeChips
            Object.keys(processedChips).map(function(key, index) {
                if (processTypeChips[key]["node"]){
                    processedChips[key] = processedChips[key]["node"];
                }
            });
            return processedChips
        },
    }
});
window.onload=function(){
    document.getElementById("addtypebutton").addEventListener("click", function() {
        this.parentNode.__vue__.showDialogBox();
    });
}


</script>
