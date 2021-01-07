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
                        </template>

                        <template slot="md-autocomplete-empty" slot-scope="{ term }">
                        <p v-if = "term" >No link types matching "{{ term }}" were found.</p>
                        <p v-else >Type a property name.</p>
                        </template>
                    </md-autocomplete>
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
                        <label>{{propertyName}}</label>

                        <template slot="md-autocomplete-item" slot-scope="{ item }">
                        <label v-if = "item.preflabel" md-term="term" md-fuzzy-search="true">
                            {{item.preflabel}}  ({{item.class_label}})
                        </label>
                        <label v-else md-term="term" md-fuzzy-search="true">
                            {{item.label}}  ({{item.class_label}})
                        </label>
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
<style scoped lang="scss" src="../assets/css/main.scss"></style>
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
            query: null,
            propertyList: [],

            entity: null,
            entityName: null,
            entityList: [],

            status: false,
            active: false,
        };
    },
    methods: {
        // property selection methods
        showSuggestedProperties(){
            this.processAutocompleteMenu();
            this.propertyList = this.getSuggestedProperties(this.uri);
        },
        resolveProperty(query){
            console.log(query);
            if (!query.label) {
                this.propertyList = this.getPropertyList(query);
                    
            }
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
            if (!query.label) {
                if (query.length > 2) {
                    this.entityList = this.getEntityList(query);
                } else
                    this.entityList = this.getNeighborEntities(this.uri);
            }
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
            this.entity = null;
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
            // if (this.datatype) this.language = null;
            let entityUri = this.entity['node'];
            let propertyUri = this.property['node'];

            if (this.entity['uri']){
                entityUri = this.entity['uri'];
            }
            if (this.property['property']){
                propertyUri = this.property['property']
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
                itemListContainer[0].style['z-index'] = 12;
                return status = true
            }
        },

        async getSuggestedProperties (uri){
            const suggestedTypes = await axios.get(
                `/about?view=suggested_links&uri=${uri}`)
            return suggestedTypes.data.outgoing
        },

        async getPropertyList (query) {
            const [rdfsProperty, owlObjectProperty] = await axios.all([
                axios.get(
                `/?term=*${query}*&view=resolve&type=http://www.w3.org/1999/02/22-rdf-syntax-ns%23Property`),
                axios.get(
                `/?term=*${query}*&view=resolve&type=http://www.w3.org/2002/07/owl%23ObjectProperty`)
            ]).catch((err) => {
                throw(err)
            })
            var combinedList = owlObjectProperty.data.concat(rdfsProperty.data)
            .sort((a, b) => (a.score < b.score) ? 1 : -1);
            let grouped = this.groupBy(combinedList, "node")
            return grouped
        },

        async getNeighborEntities (uri) {
            const neighborEntities = await axios.get(
                `/about?view=neighbors&uri=${uri}`)
            return neighborEntities.data
        },

        async getEntityList (query) {
            const entityList = await axios.get(
                `/?term=*${query}*&view=resolve`)
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
