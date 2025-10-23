<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="btn btn-outline-primary btn-sm" style="border:none; background:transparent">
                <i class="bi bi-plus"></i> Add attribute
                <span class="visually-hidden">Add data about this entity.</span>
            </button>
        </slot>
    </div>

    <div>
    <!-- Bootstrap Modal -->
    <div class="modal fade" id="addAttributeModal" tabindex="-1" :class="{'show': active}" :style="{display: active ? 'block' : 'none'}" v-if="active">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header utility-dialog-box_header">
            <h5 class="modal-title">New Attribute</h5>
            <button type="button" class="btn-close" @click="onCancel" aria-label="Close"></button>
          </div>
          <div class="modal-body" style="margin:20px;">
            <div class="row g-3">
                <div class="col-md-6">
                    <!-- Datatype property autocomplete using new component -->
                    <autocomplete 
                      v-model="datatypeProperty"
                      :fetch-data="fetchDatatypePropertyData"
                      :display-field="'preflabel'"
                      :key-field="'node'"
                      @select="selectedDatatypePropertyChange"
                      placeholder="Search for datatype property"
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
                          <p v-if="query">No datatype properties matching "{{ query }}" were found.</p>
                          <p v-else>Enter a datatype property name.</p>
                          <button type="button" class="btn btn-link p-0" @click="useCustomURI">Use a custom property URI</button>         
                        </div>
                      </template>
                    </autocomplete>
                </div>
                
                <div class="col-md-6">
                    <div class="form-floating">
                        <select class="form-select" id="datatype" v-model="datatype" @change="selectedDatatypeChange">
                            <option value="">Select data type...</option>
                            <option v-for="item in Object.values(datatypes)" 
                                    :key="item.uri"
                                    :value="item.uri">
                                {{ item.label }}
                            </option>
                        </select>
                        <label for="datatype">Data type</label>
                    </div>
                </div>
                
                <div v-if="!datatype" class="col-md-6">
                    <div class="form-floating">
                        <input type="text" class="form-control" id="language" v-model="language" placeholder="Language">
                        <label for="language">Language</label>
                    </div>
                </div>
            </div>
            
            <div v-if="useCustom" class="row g-3 mt-3">
                <div class="col">
                    <div class="form-floating">
                        <input type="text" class="form-control" id="customDatatypePropertyURI" v-model="customDatatypePropertyURI" placeholder="Full URI of datatype property">
                        <label for="customDatatypePropertyURI">Full URI of datatype property</label>
                    </div>
                </div>
            </div>
            
            <div v-if="datatypeProperty" class="row g-3 mt-3">
                <div class="col">
                    <div class="form-floating" v-if="(datatype==null)||(datatypes[datatype] && datatypes[datatype].widget=='textarea')">
                        <textarea class="form-control" 
                                  id="valueTextarea"
                                  v-model="value" 
                                  style="height: 100px"
                                  :placeholder="datatypeProperty.preflabel || datatypeProperty.label || 'Value'"></textarea>
                        <label for="valueTextarea">{{ datatypeProperty.preflabel || datatypeProperty.label || 'Value' }}</label>
                    </div>
                    <div class="form-floating" v-else>
                        <input :type="datatypes[datatype] ? datatypes[datatype].widget : 'text'" 
                               class="form-control" 
                               id="valueInput"
                               v-model="value" 
                               :placeholder="datatypeProperty.preflabel || datatypeProperty.label || 'Value'">
                        <label for="valueInput">{{ datatypeProperty.preflabel || datatypeProperty.label || 'Value' }}</label>
                    </div>
                </div>
            </div>
            
            <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary" @click.prevent="onCancel">
                    Cancel
                </button>
                <button type="button" class="btn btn-primary" @click.prevent="onSubmit">
                    Add Attribute
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

export default Vue.component('add-attribute', {
    props: ['uri', 'hideButton'],
    data: function() {
        return {
            id: null,
            datatypeProperty: null,
            datatypePropertyName: null,
            useCustom: false,
            customDatatypePropertyURI: null,
            query: null,
            awaitingResolve: false,
            propertyList: [],
            value: null,
            datatype: null,
            language: null,
            status: false,
            active: false,
            datatypes: {
                null : {
                    uri: null,
                    label: "None",
                    widget : "textarea"
                },
                'http://www.w3.org/2001/XMLSchema#string' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#string',
                    label: "String",
                    widget : "textarea"
                },
                'http://www.w3.org/2001/XMLSchema#date' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#date',
                    label: "Date",
                    widget : "date"
                },
                'http://www.w3.org/2001/XMLSchema#dateTime' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#dateTime',
                    label: "DateTime",
                    widget : "date"
                },
                'http://www.w3.org/2001/XMLSchema#integer' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#integer',
                    label: "Integer",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#decimal' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#decimal',
                    label: "Decimal",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#time' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#time',
                    label: "Time",
                    widget : "time"
                },
                'http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML' : {
                    uri: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML',
                    label: "HTML",
                    widget : "textarea"
                },
                'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral' : {
                    uri: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral',
                    label: "XML",
                    widget : "textarea"
                },
                'http://www.w3.org/2001/XMLSchema#boolean' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#boolean',
                    label: "Boolean",
                    widget : "select",
                    options : ['true', 'false']
                },
                'http://www.w3.org/2001/XMLSchema#byte' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#byte',
                    label: "Byte",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#double' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#double',
                    label: "Double",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#float' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#float',
                    label: "Float",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#int' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#int',
                    label: "Int",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#negativeInteger' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#negativeInteger',
                    label: "Integer",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#positiveInteger' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#positiveInteger',
                    label: "Integer",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#nonNegativeInteger' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#nonNegativeInteger',
                    label: "Integer",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#nonPositiveInteger' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#nonPositiveInteger',
                    label: "Integer",
                    widget : "number"
                },
                'http://www.w3.org/2001/XMLSchema#short' : {
                    uri: 'http://www.w3.org/2001/XMLSchema#short',
                    label: "Short Integer",
                    widget : "number"
                },
                'http://www.opengis.net/ont/geosparql#wktLiteral' : {
                    uri: 'http://www.opengis.net/ont/geosparql#wktLiteral',
                    label: "WKT Geometry",
                    widget: "textarea"
                },
                'http://www.opengis.net/ont/geosparql#gmlLiteral' : {
                    uri: 'http://www.opengis.net/ont/geosparql#gmlLiteral',
                    label: "GML Geometry",
                    widget: "textarea"
                }
            }
        };
    },
    methods: {
        async fetchDatatypePropertyData(query) {
            if (query && query.length > 2) {
                try {
                    return await this.getDatatypePropertyList(query);
                } catch (error) {
                    console.error('Error fetching datatype properties:', error);
                    return [];
                }
            } else {
                // Return suggested datatype properties for initial display
                return await this.getSuggestedDatatypeProperties(this.uri);
            }
        },
        useCustomURI(){
            this.useCustom = true;
            this.datatypeProperty = "Custom datatype property"
        },
        selectedDatatypePropertyChange(item){
            this.datatypeProperty = item;
            if(item.preflabel){
                this.datatypePropertyName = item.preflabel;
            } else {
                this.datatypePropertyName = item.label; 
            }
            if (item.range && this.datatypes[item.range]) {
                this.datatype = item.range;
            }
        },
        selectedDatatypeChange(item){
            console.log(this);
        },
        // Create dialog boxes
        showDialogBox () {
            this.active=true;
        },
        resetDialogBox(){
            this.active = !this.active;
            this.datatypeProperty = null;
            this.datatypePropertyName = null;
            this.useCustom = false;
            this.customDatatypePropertyURI = null;
            this.value = null;
            this.language = null;
            this.datatype = null;
        },
        onCancel() {
            return this.resetDialogBox();
        },
        onSubmit() {
            this.saveAttribute()
            .then(() => window.location.reload());
            return this.resetDialogBox();
        },
        async saveAttribute () {
            let p = Promise.resolve()
            let jsonLd = {
                '@id': this.uri
            }
            if (this.datatype) this.language = null;
            
            let propertyUri = null;
            if (this.datatypeProperty && this.datatypeProperty.node){
                propertyUri = this.datatypeProperty.node;
            } else if (this.customDatatypePropertyURI){
                propertyUri = this.customDatatypePropertyURI;
            }
            
            if (propertyUri) {
                jsonLd[propertyUri] = {
                    "@value" : this.value,
                    "@lang" : this.language,
                    "@type" : this.datatype
                }
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

        async getSuggestedDatatypeProperties (uri){
            const suggestedProperties = await axios.get(
                `${ROOT_URL}about?view=suggested_attributes&uri=${uri}`)
            return suggestedProperties.data
        },

        async getDatatypePropertyList (query) {
	    var combinedList = [];
            const [rdfsProperty, owlDatatypeProperty] = await axios.all([
                axios.get(
                `${ROOT_URL}about?term=*${query}*&view=resolve&type=http://www.w3.org/1999/02/22-rdf-syntax-ns%23Property`),
                axios.get(
                `${ROOT_URL}about?term=*${query}*&view=resolve&type=http://www.w3.org/2002/07/owl%23DatatypeProperty`)
            ]).catch((err) => {
                throw(err)
            })
            combinedList = owlDatatypeProperty.data.concat(rdfsProperty.data)
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
