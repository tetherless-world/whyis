<template>
<div>
    <div v-if="!hideButton" v-on:click="showDialogBox" >
        <slot>
            <!--Default button -->
            <button class="md-button-icon">
                <i>+ Add attribute</i>
            <md-tooltip>Add data about this entity.</md-tooltip>
            </button>
        </slot>
    </div>

    <div>
    <md-dialog :md-active.sync="active"  :md-click-outside-to-close="true">
        <div class="utility-dialog-box_header" >
            <md-dialog-title> New Attribute</md-dialog-title>
        </div>
        <div style="margin:20px;">
            <div class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-autocomplete
                        :value="attributeName"
                        :md-options="propertyList"
                        :md-open-on-focus="true"
                        @md-changed="resolveAttribute"
                        v-on:md-selected="selectedAttributeChange"
                        @md-opened="showSuggestedAttributes"
                    >
                        <label>Attribute</label>

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
                        <p v-if = "term" >No attributes matching "{{ term }}" were found.</p>
                        <p v-else >Type a property name.</p>
                        <a v-on:click="useCustomURI" style="cursor: pointer">Use a custom attribute URI</a> 
                        </template>
                    </md-autocomplete>
                </div>
                <div class="md-layout-item md-size-20">
                    <md-field>
                        <label>Data type</label>
                        <md-select
                            v-model="datatype"
                            v-on:md-selected="selectedDatatypeChange"
                            name="datatype">
                            <md-option v-for="item in datatypes"
                                    v-bind:key="item.uri"
                                    v-bind:value="item.uri">
                                {{item.label}}
                            </md-option>
                        </md-select>
                    </md-field>
                </div>
                <div v-if="!datatype" class="md-layout-item  md-size-20">
                    <md-field >
                        <label>Language</label>
                        <md-input v-model="language"></md-input>
                    </md-field>
                </div>
            </div>
            <div v-if="useCustom" class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-field >
                        <label>Full URI of attribute</label>
                        <md-input v-model="customAttributeURI"></md-input>
                    </md-field>
                </div>
            </div>
            <div v-if="attribute" class="md-layout md-gutter">
                <div class="md-layout-item">
                    <md-field >
                        <label v-if="attribute.label">{{attribute.label}}</label>
                        <label v-else>Value</label>
                        <md-textarea v-if="(datatype==null)||(datatypes[datatype].widget=='textarea')" 
                            v-model="value" md-autogrow></md-textarea>
                        <md-input v-else v-model="value" :type=datatypes[datatype].widget> </md-input>
                    </md-field>
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
                    Add Attribute
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

export default Vue.component('add-attribute', {
    props: ['uri', 'hideButton'],
    data: function() {
        return {
            id: null,
            attribute: null,
            attributeName: null,
            useCustom: false,
            customAttributeURI: null,
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
        showSuggestedAttributes(){
            this.processAutocompleteMenu();
        },
        useCustomURI(){
            this.useCustom = true;
            this.attribute = "Custom attribute"
        },
        resolveAttribute(query){
            var thisVue = this;
            this.query = query;
            if (!thisVue.awaitingResolve) {
                setTimeout(function () {
                    console.log(thisVue.query);
                    if (!thisVue.query.label) {
                        if (thisVue.query.length > 2) {
                            thisVue.propertyList = thisVue.getAttributeList(thisVue.query);
                        } else
                            thisVue.propertyList = thisVue.getSuggestedAttributes(thisVue.uri);
                    }
                    thisVue.awaitingResolve = false;
                }, 1000);   
            }
            thisVue.awaitingResolve = true;
        },
        selectedAttributeChange(item){
            this.attribute = item;
            console.log(item);
            if (item.range && this.datatypes[item.range]) {
                this.datatype = this.datatypes[item.range];
            }
            console.log(this);
        },
        selectedDatatypeChange(item){
            console.log(this);
        },
        // Create dialog boxes
        showDialogBox () {
            this.propertyList = this.getSuggestedAttributes(this.uri);
            this.active=true;
        },
        resetDialogBox(){
            this.active = !this.active;
            this.attribute = null;
            this.attributeName = null;
            this.useCustom = false;
            this.customAttributeURI = null;
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
            if (this.attribute.node){
                jsonLd[this.attribute.node] = {
                    "@value" : this.value,
                    "@lang" : this.language,
                    "@type" : this.datatype
                }
            }
            else if (this.customAttributeURI){
                jsonLd[this.customAttributeURI] = {
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
            const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
            if(itemListContainer.length >= 1) {
                //itemListContainer[0].style['z-index'] = 12;
                return status = true
            }
        },

        async getSuggestedAttributes (uri){
            const suggestedTypes = await axios.get(
                `${ROOT_URL}about?view=suggested_attributes&uri=${uri}`)
            return suggestedTypes.data
        },

        async getAttributeList (query) {
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
