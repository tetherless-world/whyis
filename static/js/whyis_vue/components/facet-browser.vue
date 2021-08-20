<template>
<div>
  <md-progress-bar v-if="isLoadingResults" md-mode="indeterminate"></md-progress-bar>
  <span v-if="updateError" class="md-error md-accent" style="color:red">Unable to run query. Please verify selections and remove any duplicated facet values</span>
  <!-- <uib-alert flex ng-if="error" type="danger"><span ng-bind="error"></span></uib-alert> -->
  <div layout="row" flex>
    <md-content flex="30" style="overflow:scroll">
      <md-subheader>
          <span ng-show="processedResults.data.values.length">{{processedResults.data.values.length}} results found.</span>
          <md-button :disabled="isLoadingResults"  class=" md-mini md-primary"
                     aria-label="Update"
                     title="Update Results"
                     v-on:click="updateResults()">
            Update
          </md-button>

          <!-- <md-progress-circular ng-show="vm.isLoadingResults" md-diameter="20px"></md-progress-circular> -->
      </md-subheader>
        <div v-if="facetsLoaded"> 
            <div v-for="(facet, index) in facets" 
                v-bind:key="index + 'facet'" >
                <smart-facet v-bind:facetobject="facet" @selected-facets-changed="onFacetsChanged"></smart-facet>
            
            <!-- <md-progress-bar md-mode="indeterminate" ng-show="this.isLoading()"></md-progress-bar> -->
            <!-- <md-toolbar class="md-warn" ng-if="vm.error">
                <div class="md-toolbar-tools">
                <h2 class="md-flex">{{ vm.error|limitTo:100 }}</h2>
                </div>
            </md-toolbar> -->
            </div>
        </div>
    </md-content>

    </div>
    <div v-if="show_yasr">
        <yasr v-bind:results="sparqlResults"></yasr>
    </div>
</div>
</template>
<style scoped lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
import axios from 'axios'

export default Vue.component('facet-browser', {
    props: {
        show_yasr: {
            default: true,
            type: Boolean
        },
        class_uri: {
            default: "http://materialsmine.org/ns/Metamaterial",
            type: String
        },
    },
    data: function() {
        return {
            isLoadingResults: false,
            updateError: false,
            facetsLoaded: false,
            sparqlQuery: "",
            sparqlResults: {},
            processedResults: {
                "data": {
                    "values":[],
                },
            },
            scope: {
                type : "=",
                constraints : "=?",
                title : "=?",
                vizConfig: null,
            },
            facetValues: {},
            facets: [
                // {
                //     facetId: 'type',
                //     predicate:'rdf:type/rdfs:subClassOf*',
                //     hierarchy: 'rdfs:subClassOf',
                //     depth: '5',
                //     specifier: 'FILTER (!ISBLANK(?value) && !strstarts(str(?value), "bnode:") )',
                //     preferredLang: "en",
                //     enabled: true,
                //     classes: ['<'+type+'>'],
                //     type: 'hierarchy',
                //     name: 'Type'
                // }
            ],
        }
    },
    methods: {
        onFacetsChanged(facetData){
            this.facetValues[facetData.facet] = facetData.facetvalues;
            console.log(facetData);
        },
        async updateResults() {
            this.isLoadingResults = true;
            this.updateError = false;
            var this_vue = this
            await this.runSparqlQuery()
                .then( response => {
                    if(this_vue.updateError){
                        this.isLoadingResults = false;
                    }
                    this.$emit('facet-browser-update', {fbquery: this.sparqlQuery, fbresults: this.sparqlResults});
                })
                .catch(function(e){console.error(e.message)})
        },
        // Disable the facets while results are being retrieved.
        disableFacets() {
            return this.isLoadingResults;
        },
        // Get the selected values from the nested dictionary
        getFacetSelections() {
            var selections = [];
            var valuesPerFacet = Object.values(this.facetValues);
            var facetValues = Object.values(valuesPerFacet)
            facetValues.forEach(function(value){
                selections = selections.concat(value)
            });
            return selections;
        },
        // Get facets for this class
        async getFacets() {
            var res = {};
            return await axios.get(`/about?view=facets&uri=${encodeURIComponent(this.class_uri)}`, {
                headers: {
                    'Accept': 'application/json',
                }
            })
            .then(response => {
                let responseData = []
                if (!response) {
                    return res;
                }
                try {
                    responseData = response.data;
                }
                catch(e) {
                    console.error(e)
                }
                Object.keys(responseData).forEach(function(key, index) {
                    let facet_id = responseData[key]['facetId']
                    res[facet_id] = responseData[key];
                    res[facet_id]['values'] = [];
                });
                return [res, responseData];
            })
            
        },
        // Get facet values for this class and assign to facets
        async getFacetValues() {
            var vals = {};
            let this_vue = this
            return await axios.get(`/about?view=facet_values&uri=${encodeURIComponent(this.class_uri)}`, {
                headers: {
                    'Accept': 'application/json',
                }
            })
            .then(response => {
                if (!response) {
                    return vals;
                }
                try {
                    response = response.data;
                }
                catch(e) {
                    response = vals;
                }
                Object.keys(response).forEach(function(key, index) {
                    var facetValueInstance = response[key];
                    let facet_id = facetValueInstance['facetId']
                    // Otherwise throws an error if no specifier is present
                    if(!facetValueInstance['specifier']) {
                        facetValueInstance['specifier'] = "";
                    }
                    if (this_vue.facets[facet_id]['values']) {
                        this_vue.facets[facet_id]['values'].push(facetValueInstance)
                    }
                    else {
                        this_vue.facets[facet_id]['values'] = [facetValueInstance]
                    }
                });
                return vals;
            })
            
        },
        async runSparqlQuery(){
            let this_vue = this;
            var facetSelections = this.getFacetSelections();
            var filteredVariables = facetSelections.filter(function(v) { return !v.indep_val})
            await axios.get('/about', {
                params: {
                    uri: this.class_uri,
                    view:'instance_data',
                    // constraints: JSON.stringify(facetSelections.constraint),
                    variables: JSON.stringify(filteredVariables)
                },
                responseType:'text'
            })
            .then(function(response) {
                this_vue.sparqlQuery = response.data;
                console.log("query", this_vue.sparqlQuery);
                return axios
                    .get(ROOT_URL+'sparql', {params : {query : this_vue.sparqlQuery, output: 'json'}, responseType: 'json'})
                    .then(function(response) {
                        this_vue.sparqlResults = response.data
                        this_vue.processedResults.data = { values: this_vue.transformSparqlData(response.data) };
                        filteredVariables.forEach(function(facetValue) {
                            if (facetValue.type != "nominal") {
                                // var extent = d3.extent(this_vue.processedResults.data.values,
                                //                         d => d[facetValue.field]);
                                var fieldValues = this_vue.processedResults.data.values.map(d => d[facetValue.field])
                                var minExtent = Math.min(...fieldValues)
                                var maxExtent = Math.max(...fieldValues)
                                // facetValue.min = extent[0];
                                facetValue.min = minExtent
                                if (facetValue.lower === undefined) {
                                    facetValue.lower = facetValue.min;
                                }
                                // facetValue.max = extent[1];
                                facetValue.max = maxExtent
                                if (facetValue.upper === undefined) {
                                    facetValue.upper = facetValue.max;
                                }
                                console.log(facetValue);
                            }
                        })
                        this_vue.isLoadingResults = false;
                    })
                    .catch(function(e) {
                        console.error(e.message);
                        this_vue.updateError = true;
                        return e
                    });
            });
        },
        transformSparqlData(sparqlResults){
            let converters = {
                "http://www.w3.org/2001/XMLSchema#integer" : JSON.parse,
                "http://www.w3.org/2001/XMLSchema#double" : JSON.parse,
                "http://www.w3.org/2001/XMLSchema#float" : JSON.parse,
                "http://www.w3.org/2001/XMLSchema#decimal" : JSON.parse,
                "http://www.w3.org/2001/XMLSchema#boolean" : JSON.parse
            }

            function fromRdf(value, datatype) {
                if (converters[datatype])
                    return converters[datatype](value);
                return value;
            }

            const data = []
            if (sparqlResults) {
                for (const row of sparqlResults.results.bindings) {
                    const resultData = {}
                    data.push(resultData)
                    Object.entries(row).forEach(([field, result, t]) => {
                        let value = result.value
                        if (result.type === 'literal' && result.datatype) {
                            value = fromRdf(value, result.datatype)
                        }
                        resultData[field] = value
                    })
                }
            }
            return data
        },
        processConstraints(response) {
            var facetsTemp = {}
            var facetProcessors = {
                'http://www.w3.org/2002/07/owl#ObjectProperty' : function(d) {
                    d.name = d.label;
                    if (!d.facetId)
                        d.facetId = b64_sha256(d.property);
                    if (!d.predicate) {
                        d.predicate = '<'+d.property+'>';
                        if (d.inverse) {
                            d.predicate = '('+d.predicate+ '|<' + d.inverse + '>)';
                        }
                    }
                    d.entityPredicate = d.predicate;
                    if (d.typeProperty === undefined) {
                        d.typeProperty = 'rdf:type';
                    }
                    if (d.typeProperty != '') {
                        d.predicate = d.predicate + '/' + d.typeProperty;
                    }
                    d.enabled = true;
                    d.preferredLang = "en";
                    if (!d.type)
                        d.type = "basic";
                    // if (!d.specifier)
                    //     d.specifier = '';
                },
                'http://www.w3.org/2002/07/owl#DatatypeProperty' : function(d) {
                    d.name = d.label;
                    if (!d.facetId)
                        d.facetId = b64_sha256(d.property);
                    if (!d.predicate) {
                        d.predicate = '<'+d.property+'>';
                    }
                    d.enabled = true;
                    d.preferredLang = "en";
                    if (!d.type) {
                        if (d.count > 1000) {
                            d.type = "text";
                        } else {
                            d.type = "basic";
                        }
                    }
                },
                'http://semanticscience.org/resource/Quality' : function(d) {
                    d.name = "Qualities";
                    if (!d.facetId)
                        d.facetId = b64_sha256(d.property)+'/'+b64_sha256('http://semanticscience.org/resource/Quality');
                    if (!d.predicate) {
                        d.predicate = '<'+d.property+'>';
                        if (d.inverse) {
                            d.predicate = '('+d.predicate+ '|<' + d.inverse + '>)';
                        }
                    }
                    d.entityPredicate = d.predicate;
                    if (!d.typeProperty) {
                        d.typeProperty = 'rdf:type';
                    }
                    d.predicate = d.predicate + '/' + d.typeProperty;
                    d.specifier = '?value rdfs:subClasOf <http://semanticscience.org/resource/Quality>.\n';
                    d.enabled = true;
                    d.preferredLang = "en";
                    if (!d.type)
                        d.type = "basic";
                },
                'http://semanticscience.org/resource/Quantity' : function(d) {
                    d.name = "Properties";
                    if (!d.facetId)
                        d.facetId = b64_sha256(d.property)+'/'+b64_sha256('http://semanticscience.org/resource/Quantity');
                    if (!d.predicate) {
                        d.predicate = '<'+d.property+'>';
                        if (d.inverse) {
                            d.predicate = '('+d.predicate+ '|<' + d.inverse + '>)';
                        }
                    }
                    d.entityPredicate = d.predicate;
                    if (!d.typeProperty) {
                        d.typeProperty = 'rdf:type';
                    }
                    d.predicate = d.predicate + '/' + d.typeProperty;
                    d.specifier = '?value rdfs:subClassOf <http://semanticscience.org/resource/Quantity>.\n';
                    d.enabled = true;
                    d.preferredLang = "en";
                    if (!d.type)
                        d.type = "basic";
                }
            }
            response.forEach(function (d) {
                if (facetProcessors[d.propertyType] != null) {
                    facetProcessors[d.propertyType](d);
                    facetsTemp[d.facetId] = d;
                }
            });
            return facetsTemp
        },

    },
    created: function () {
        this.getFacets()
        .then( facetResponse  =>{
            this.facets = this.processConstraints(facetResponse[1])
            this.getFacetValues()
            .then( valuesResponse => {
                this.facetValues = valuesResponse
                this.facetsLoaded = true
                this.runSparqlQuery()
            })
            
        });
    },
});

</script>
