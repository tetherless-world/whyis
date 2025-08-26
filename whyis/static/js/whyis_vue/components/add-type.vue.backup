<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="md-button-icon"
                style="border:none; background:transparent">
                <i>+ Add type(s)</i>
            <md-tooltip>Specify additional type, subclass, or superclass.</md-tooltip>
            </button>
        </slot>
    </div>
    
    <div>
    <md-dialog :md-active.sync="active" :md-click-outside-to-close="true">
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
                @md-closed="processAutocompleteMenu(true)"
            >
                <label>Search for types</label>

                <template style="width: 90% !important; left: 1px !important;" slot="md-autocomplete-item" slot-scope="{ item }">
                <label v-if = "item.preflabel" md-term="term" md-fuzzy-search="true">
                    {{item.preflabel}}
                </label>
                <label v-else md-term="term" md-fuzzy-search="true">
                    {{item.label}}
                </label>
                <md-tooltip>{{item.node}}{{item.property}}</md-tooltip>
                </template>
            
                <template style="width: 90% !important; left: 1px !important" slot="md-autocomplete-empty" slot-scope="{ term }">
                <p v-if="term">No types or classes matching "{{ term }}" were found.</p>
                <p v-else> Enter a type name.</p>
                <a v-on:click="useCustomURI" style="cursor: pointer">Use a custom type URI</a>         
                </template>
            </md-autocomplete>
            <div v-if="useCustom" class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-field>
                        <label>Full URI of type</label>
                        <md-input v-model="customTypeURI"></md-input>
                    <md-button v-on:click="submitCustomURI" class="md-raised">
                        Confirm URI
                    </md-button>
                    </md-field>
                </div>
            </div>
            <div
                v-for="(chip, key) in typeChips" 
                v-bind:key="key + 'chips'">
                <md-chip class="md-layout md-alignment-center-left" v-model=typeChips[key] 
                    style="margin-bottom:4px; max-width:fit-content">
                    <div class="md-layout-item" style="max-width:fit-content">
                        <div v-if= "typeChips[key].preflabel">
                            {{typeChips[key].preflabel}}
                        </div>
                        <div v-else>
                            {{typeChips[key].label}}
                        </div>
                    </div>
                    <div class="md-layout-item" style="max-width:fit-content">
                        <button @click="removeChip(key)" style="border:none; border-radius:50%; margin-left:4px">x</button>
                    </div>
                </md-chip>
            </div>
        
            <div class="utility-margin-big viz-2-col">
                <div class="utility-align--right utility-margin-top">
                </div>
                <div class="utility-align--right utility-margin-top">
                <md-button @click.prevent="onCancel" class="md-raised">
                    Cancel
                </md-button>
                <md-button @click.prevent="onSubmit" class="md-raised">
                    Submit
                </md-button>
                </div>
            </div>
        </div>
    </md-dialog>
    </div>
</div>
</template>
<style lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import axios from 'axios'
import { postNewNanopub } from '../utilities/nanopub'

export default Vue.component('add-type', {
    props: ['uri', 'hideButton'],
    data: function() {
        return {
            id: null,
            useCustom: false,
            customTypeURI: null,
            typeList: [],
            selectedType: null,
            typeChips: [],
            status: false,
            active: false,
            query: null,
            awaitingResolve: false,
        };
    },
    methods: {
        showSuggestedTypes(){
            this.processAutocompleteMenu();
            this.typeList = this.getSuggestedTypes(this.uri);
        },
        useCustomURI(){
            this.useCustom = true;
        },
        submitCustomURI(){
            var newChip = {
                label: this.customTypeURI,
                node: this.customTypeURI, 
            }
            this.typeChips.push(newChip);
            this.customTypeURI = "";
            this.useCustom = false
        },
        resolveEntityType(query){
            var thisVue = this;
            this.query = query
            if (!thisVue.awaitingResolve) {
                setTimeout(function () {
                    console.log(thisVue.query)
                    thisVue.typeList = thisVue.getTypeList(thisVue.query);
                    thisVue.awaitingResolve = false;
                }, 1000); 
            }
            thisVue.awaitingResolve = true;
        },
        selectedTypeChange(item){
            this.typeChips.push(item);
        },
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
        },
        removeChip(index){
            this.typeChips.splice(index, 1);
        },
        resetDialogBox(){
            this.active = !this.active;
            this.typeChips = [];
            this.customTypeURI = "";
            this.useCustom = false;
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.saveNewTypes()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        },
        async saveNewTypes () {
            let p = Promise.resolve()
            const types = this.processTypeChips();
            const jsonLd = {
                '@id': this.uri,
                '@type': types, 
            }
            await p
            try{
                return postNewNanopub(jsonLd)
            } catch(err){
                return alert(err)
            }
        },
        processTypeChips () {
            var processedChips = this.typeChips
            Object.keys(processedChips).map(function(key, index) {
                if (processedChips[key]["node"]){
                    processedChips[key] = processedChips[key]["node"];
                }
            });
            return processedChips
        },
        // Formats the dropdown menu. Runs only while the menu is open
        processAutocompleteMenu (param) {
            const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
            if(itemListContainer.length >= 1) {
                //itemListContainer[0].style['z-index'] = 12;
                return status = true
            }
        },

        async getSuggestedTypes (uri){
            const suggestedTypes = await axios.get(
                `${ROOT_URL}about?view=suggested_types&uri=${uri}`)
            return suggestedTypes.data
        },

        async getTypeList (query) {
            var combinedList = [];
            const [rdfsClass, owlClass] = await axios.all([
                axios.get(
                `${ROOT_URL}about?term=${query}*&view=resolve&type=http://www.w3.org/2000/01/rdf-schema%23Class`),
                axios.get(
                `${ROOT_URL}about?term=${query}*&view=resolve&type=http://www.w3.org/2002/07/owl%23Class`)
            ]).catch((err) => {
                throw(err)
            })
            combinedList = owlClass.data.concat(rdfsClass.data)
            .sort((a, b) => (a.score < b.score) ? 1 : -1);
            let grouped = this.groupBy(combinedList, "node")
            return grouped
        },

        // Group entries by the value of a particular key
        groupBy (original, key) {
            let groupedDictionary = original.reduce(function(grouped, index) {
                grouped[index[key]] = grouped[index[key]] || index;
                return grouped;
            }, {});
            var values = Object.keys(groupedDictionary).map(function(key) {
                return groupedDictionary[key]
            })
            return values
        },
    },
    created: function () {
        // If the component was called with hideButton enabled,
        // render the dialog box without needing a click from the button component
        if(this.hideButton){
            this.active=true;
        }
    }
});

</script>
