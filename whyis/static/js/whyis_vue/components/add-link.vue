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
    <div class="modal fade" id="addLinkModal" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header utility-dialog-box_header">
            <h5 class="modal-title">New Link</h5>
            <button type="button" class="btn-close" @click="onCancel" aria-label="Close"></button>
          </div>
          <div class="modal-body" style="margin:20px;">
            <div class="mb-3">
                <!-- Property autocomplete using new component -->
                <autocomplete 
                  v-model="property"
                  :fetch-data="fetchPropertyData"
                  :display-field="'preflabel'"
                  :key-field="'node'"
                  @select="selectedPropertyChange"
                  placeholder="Link Type"
                  input-class="form-control">
                  <template #option="{ item }">
                    <div>
                      <span v-if="item.preflabel">{{ item.preflabel }}</span>
                      <span v-else>{{ item.label }}</span>
                      <small class="text-muted d-block">{{ item.node || item.property }}</small>
                    </div>
                  </template>
                  <template #no-results="{ query }">
                    <div class="alert alert-info mt-2">
                      <p v-if="query">No link types matching "{{ query }}" were found.</p>
                      <p v-else>Type a property name.</p>
                      <button type="button" class="btn btn-link p-0" @click="useCustomURI">Use a custom property URI</button> 
                    </div>
                  </template>
                </autocomplete>
            </div>
            
            <div v-if="useCustom" class="mb-3">
                <div class="form-floating">
                    <input type="text" class="form-control" id="customPropertyURI" v-model="customPropertyURI" placeholder="Full URI of property">
                    <label for="customPropertyURI">Full URI of property</label>
                </div>
            </div>
            
            <div v-if="property" class="mb-3">
                <!-- Entity autocomplete using new component -->
                <autocomplete 
                  v-model="entity"
                  :fetch-data="fetchEntityData"
                  :display-field="'preflabel'"
                  :key-field="'node'"
                  @select="selectedEntityChange"
                  :placeholder="propertyName || 'Linked entity'"
                  input-class="form-control">
                  <template #option="{ item }">
                    <div>
                      <span v-if="item.preflabel">{{ item.preflabel }} ({{ item.class_label }})</span>
                      <span v-else>{{ item.label }} ({{ item.class_label }})</span>
                      <small class="text-muted d-block">{{ item.node || item.uri }}</small>
                    </div>
                  </template>
                  <template #no-results="{ query }">
                    <div class="alert alert-info mt-2">
                      <p v-if="query">No entities matching "{{ query }}" were found.</p>
                      <p v-else>Type an entity name.</p>
                    </div>
                  </template>
                </autocomplete>
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
            useCustom: false,
            customPropertyURI: null,

            entity: null,

            status: false,
            active: false,
        };
    },
    methods: {
        useCustomURI(){
            this.useCustom = true;
            this.property = "Custom attribute"
        },
        // Property and entity fetch methods for autocomplete
        async fetchPropertyData(query) {
            if (query && query.length > 2) {
                try {
                    return await this.getPropertyList(query);
                } catch (error) {
                    console.error('Error fetching properties:', error);
                    return [];
                }
            } else {
                // Return suggested properties for initial display
                return await this.getSuggestedProperties(this.uri);
            }
        },
        async fetchEntityData(query) {
            if (query && query.length > 2) {
                try {
                    return await this.getEntityList(query);
                } catch (error) {
                    console.error('Error fetching entities:', error);
                    return [];
                }
            } else {
                // Return neighbor entities for initial display  
                return await this.getNeighborEntities(this.uri);
            }
        },
        selectedPropertyChange(item){
            this.property = item;
            if(item.preflabel){
                this.propertyName = item.preflabel;
            }
            else {this.propertyName = item.label; }
        },
        selectedEntityChange(item){
            this.entity = item;
        },
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
        },
        resetDialogBox(){
            this.active = !this.active;
            this.property = null;
            this.propertyName = null;
            this.useCustom = false;
            this.customPropertyURI = null;
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
