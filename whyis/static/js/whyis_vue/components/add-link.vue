<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="md-button-icon">
                <i>+ Add Link</i>
            <md-tooltip>Add a link to another entity.</md-tooltip>
            </button>
        </slot>
    </div>

    <div>
    <md-dialog :md-active.sync="active"  :md-click-outside-to-close="true">
        <div class="utility-dialog-box_header" >
            <md-dialog-title>New Link</md-dialog-title>
        </div>
        <div style="margin:20px;">
            <div class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-autocomplete
                        :value="propertyName"
                        :md-options="propertyList"
                        :md-open-on-focus="true"
                        @md-changed="resolveProperty"
                        v-on:md-selected="selectedPropertyChange"
                        @md-opened="showSuggestedProperties"
                    >
                        <label>Link Type</label>

                        <template slot="md-autocomplete-item" slot-scope="{ item }">
                        <label v-if = "item.preflabel" md-term="term" md-fuzzy-search="true">
                            {{item.preflabel}}
                        </label>
                        <label v-else md-term="term" md-fuzzy-search="true">
                            {{item.label}}
                        </label>
                        <md-tooltip>{{item.node}}{{item.property}}</md-tooltip>
                        </template>

                        <template slot="md-autocomplete-empty" slot-scope="{ term }">
                        <p v-if = "term" >No link types matching "{{ term }}" were found.</p>
                        <p v-else >Type a property name.</p>
                        <a v-on:click="useCustomURI" style="cursor: pointer">Use a custom property URI</a> 
                        </template>
                    </md-autocomplete>
                </div>
            </div>
            <div v-if="useCustom" class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-field >
                        <label>Full URI of property</label>
                        <md-input v-model="customPropertyURI"></md-input>
                    </md-field>
                </div>
            </div>
            <div v-if="property" class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-autocomplete
                        :value="entityName"
                        :md-options="entityList"
                        :md-open-on-focus="true"
                        @md-changed="resolveEntity"
                        v-on:md-selected="selectedEntityChange"
                        @md-opened="showNeighborEntities"
                    >
                        <label v-if="propertyName">{{propertyName}}</label>
                        <label v-else>Linked entity</label>

                        <template slot="md-autocomplete-item" slot-scope="{ item }">
                        <label v-if = "item.preflabel" md-term="term" md-fuzzy-search="true">
                            {{item.preflabel}}  ({{item.class_label}})
                        </label>
                        <label v-else md-term="term" md-fuzzy-search="true">
                            {{item.label}}  ({{item.class_label}})
                        </label>
                        
                        <md-tooltip>{{item.node}}{{item.uri}}</md-tooltip>
                        </template>

                        <template slot="md-autocomplete-empty" slot-scope="{ term }">
                        <p v-if = "term" >No entities matching "{{ term }}" were found.</p>
                        <p v-else >Type an entity name.</p>
                        </template>
                    </md-autocomplete>
                </div>
            </div>
            <div class="utility-margin-big viz-2-col">
                <div class="utility-align--right utility-margin-top">
                </div>
                <div class="utility-align--right utility-margin-top">
                <md-button @click.prevent="onCancel" class="md-raised">
                    Cancel
                </md-button>
                <md-button @click.prevent="onSubmit" class="md-raised">
                    Add Link
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

export default Vue.component('add-link', {
    props: ['uri', 'hideButton'],
    data: function() {
        return {
            id: null,
            property: null,
            propertyName: null,
            propertyQuery: null,
            propertyList: [],
            useCustom: false,
            customPropertyURI: null,

            entity: null,
            entityName: null,
            entityQuery: null,
            entityList: [],

            status: false,
            active: false,
            awaitingResolve: false,
            awaitingEntity: false,
        };
    },
    methods: {
        useCustomURI(){
            this.useCustom = true;
            this.property = "Custom attribute"
        },
        // property selection methods
        showSuggestedProperties(){
            this.processAutocompleteMenu();
            this.propertyList = this.getSuggestedProperties(this.uri);
        },
        resolveProperty(query){
            var thisVue = this;
            this.propertyQuery = query
            if (!thisVue.awaitingResolve) {
                setTimeout(function () {
                    console.log(thisVue.propertyQuery);
                    if (!query.label) {
                        thisVue.propertyList = thisVue.getPropertyList(thisVue.propertyQuery);        
                    }
                    thisVue.awaitingResolve = false;
                }, 1000); 
            }
            thisVue.awaitingResolve = true;
        },
        selectedPropertyChange(item){
            this.property = item;
            if(item.preflabel){
                this.propertyName = item.preflabel;
            }
            else {this.propertyName = item.label; }
            console.log(item);
        },
        // entity selection methods
        showNeighborEntities(){
            this.processAutocompleteMenu();
            this.entityList = this.getNeighborEntities(this.uri);
        },
        resolveEntity(query){
            var thisVue = this;
            this.entityQuery = query
            // Debounce for entity search 
            if (!thisVue.awaitingEntity) {
                setTimeout(function () {
                    let entityQuery = thisVue.entityQuery;
                    if (!entityQuery.label) {
                        if (entityQuery.length > 2) {
                            thisVue.entityList = thisVue.getEntityList(entityQuery);
                        } else
                            thisVue.entityList = thisVue.getNeighborEntities(thisVue.uri);
                    }
                    thisVue.awaitingEntity = false;
                }, 1000); 
            }
            thisVue.awaitingEntity = true;
        },
        selectedEntityChange(item){
            this.entity = item;
            this.entityName = item.label;
            console.log(item);
        },
        // Create dialog boxes
        showDialogBox () {
            this.propertyList = this.getSuggestedProperties(this.uri);
            this.active=true;
        },
        resetDialogBox(){
            this.active = !this.active;
            this.property = null;
            this.propertyName = null;
            this.useCustom = false;
            this.customPropertyURI = null;
            this.entity = null;
            this.entityName = null;
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.saveLink()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        },
        async saveLink () {
            let p = Promise.resolve()
            let jsonLd = {
                '@id': this.uri
            }
            let entityUri = this.entity['node'];
            if (this.entity['uri']){
                entityUri = this.entity['uri'];
            }
            
            let propertyUri = null;
            if (this.property['node']){
                propertyUri = this.property['node'];
            }
            else if (this.property['property']){
                propertyUri = this.property['property']
            }
            else if (this.customPropertyURI){
                propertyUri = this.customPropertyURI
            }

            jsonLd[propertyUri] = {
                "@id" : entityUri,
            }
            
            console.log(jsonLd);
            await p
            try {
                return postNewNanopub(jsonLd)
            } catch(err){
                return alert(err)
            }
        },
        // Formats the dropdown menu. Runs only while the menu is open
        processAutocompleteMenu (param) {
            const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
            if(itemListContainer.length >= 1) {
                //itemListContainer[0].style['z-index'] = 12;
                return status = true
            }
        },

        async getSuggestedProperties (uri){
            const suggestedTypes = await axios.get(
                `${ROOT_URL}about?view=suggested_links&uri=${uri}`)
            return suggestedTypes.data.outgoing
        },

        async getPropertyList (query) {
	    var combinedList = [];
            const [rdfsProperty, owlObjectProperty] = await axios.all([
                axios.get(
                `${ROOT_URL}about?term=*${query}*&view=resolve&type=http://www.w3.org/1999/02/22-rdf-syntax-ns%23Property`),
                axios.get(
                `${ROOT_URL}about?term=*${query}*&view=resolve&type=http://www.w3.org/2002/07/owl%23ObjectProperty`)
            ]).catch((err) => {
                throw(err)
            })
            combinedList = owlObjectProperty.data.concat(rdfsProperty.data)
            .sort((a, b) => (a.score < b.score) ? 1 : -1);
            let grouped = this.groupBy(combinedList, "node")
            return grouped
        },

        async getNeighborEntities (uri) {
            const neighborEntities = await axios.get(
                `${ROOT_URL}about?view=neighbors&uri=${uri}`)
            return neighborEntities.data
        },

        async getEntityList (query) {
            const entityList = await axios.get(
                `${ROOT_URL}about?term=*${query}*&view=resolve`)
            return entityList.data
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
