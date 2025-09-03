<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="btn btn-outline-primary btn-sm" style="border:none; background:transparent">
                <i class="bi bi-plus"></i> Add Link
                <span class="visually-hidden">Add a link to another entity.</span>
            </button>
        </slot>
    </div>

    <div>
    <!-- Bootstrap Modal -->
    <div class="modal fade" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header utility-dialog-box_header">
            <h5 class="modal-title">New Link</h5>
            <button type="button" class="btn-close" @click="onCancel" aria-label="Close"></button>
          </div>
          <div class="modal-body" style="margin:20px;">
            <div class="mb-3">
                <!-- Property autocomplete -->
                <div class="form-floating position-relative">
                    <input type="text" 
                           class="form-control" 
                           id="propertySearch"
                           v-model="propertyName"
                           @input="resolveProperty($event.target.value)"
                           @focus="showSuggestedProperties"
                           placeholder="Link Type">
                    <label for="propertySearch">Link Type</label>
                </div>
                
                <!-- Property dropdown results -->
                <div v-if="propertyList.length > 0" class="dropdown-menu show position-absolute w-100" style="max-height: 200px; overflow-y: auto; z-index: 1060;">
                    <button v-for="item in propertyList" :key="item.node" 
                            class="dropdown-item text-start" 
                            @mousedown="selectedPropertyChange(item)">
                        <div>
                            <span v-if="item.preflabel">{{ item.preflabel }}</span>
                            <span v-else>{{ item.label }}</span>
                            <small class="text-muted d-block">{{ item.node }}{{ item.property }}</small>
                        </div>
                    </button>
                </div>
                
                <div v-if="propertyList.length === 0 && propertyName" class="alert alert-info mt-2">
                    <p v-if="propertyName">No link types matching "{{ propertyName }}" were found.</p>
                    <p v-else>Type a property name.</p>
                    <button type="button" class="btn btn-link p-0" @click="useCustomURI">Use a custom property URI</button> 
                </div>
            </div>
            
            <div v-if="useCustom" class="mb-3">
                <div class="form-floating">
                    <input type="text" class="form-control" id="customPropertyURI" v-model="customPropertyURI" placeholder="Full URI of property">
                    <label for="customPropertyURI">Full URI of property</label>
                </div>
            </div>
            
            <div v-if="property" class="mb-3">
                <!-- Entity autocomplete -->
                <div class="form-floating position-relative">
                    <input type="text" 
                           class="form-control" 
                           id="entitySearch"
                           v-model="entityName"
                           @input="resolveEntity($event.target.value)"
                           @focus="showNeighborEntities"
                           :placeholder="propertyName || 'Linked entity'">
                    <label for="entitySearch">{{ propertyName || 'Linked entity' }}</label>
                </div>
                
                <!-- Entity dropdown results -->
                <div v-if="entityList.length > 0" class="dropdown-menu show position-absolute w-100" style="max-height: 200px; overflow-y: auto; z-index: 1060;">
                    <button v-for="item in entityList" :key="item.node || item.uri" 
                            class="dropdown-item text-start" 
                            @mousedown="selectedEntityChange(item)">
                        <div>
                            <span v-if="item.preflabel">{{ item.preflabel }} ({{ item.class_label }})</span>
                            <span v-else>{{ item.label }} ({{ item.class_label }})</span>
                            <small class="text-muted d-block">{{ item.node }}{{ item.uri }}</small>
                        </div>
                    </button>
                </div>
                
                <div v-if="entityList.length === 0 && entityName" class="alert alert-info mt-2">
                    <p v-if="entityName">No entities matching "{{ entityName }}" were found.</p>
                    <p v-else>Type an entity name.</p>
                </div>
            </div>
            
            <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" @click.prevent="onCancel">
                    Cancel
                </button>
                <button type="button" class="btn btn-primary" @click.prevent="onSubmit">
                    Add Link
                </button>
            </div>
          </div>
        </div>
      </div>
    </div>
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
            const itemListContainer = document.getElementsByClassName("dropdown-menu")
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
