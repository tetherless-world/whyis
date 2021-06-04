<template>
<div style="width:25%">
  <md-progress-bar v-if="isLoadingResults" md-mode="indeterminate"></md-progress-bar>
  <!-- <uib-alert flex ng-if="error" type="danger"><span ng-bind="error"></span></uib-alert> -->
  <div layout="row" flex>
    <md-content flex="30" style="overflow:scroll">
      <md-subheader>
          <span ng-show="vizConfig.data.values.length">{{vizConfig.data.values.length}} results found.</span>
          <md-button ng-disabled="!updatable"  class=" md-mini md-primary"
                     aria-label="Update"
                     title="Update Results"
                     data-ng-click="updateResults(null, cons)">
            Update
          </md-button>

          <!-- <md-progress-circular ng-show="vm.isLoadingResults" md-diameter="20px"></md-progress-circular> -->
      </md-subheader>
        <div v-for="(facet, index) in facets" 
              v-bind:key="index + 'facet'" >
            <smart-facet v-bind:facetobject="facet"></smart-facet>
          
          <!-- <md-progress-bar md-mode="indeterminate" ng-show="this.isLoading()"></md-progress-bar> -->
          <!-- <md-toolbar class="md-warn" ng-if="vm.error">
            <div class="md-toolbar-tools">
              <h2 class="md-flex">{{ vm.error|limitTo:100 }}</h2>
            </div>
          </md-toolbar> -->
        </div>
    </md-content>

 </div>
</div>
</template>
<style scoped lang="scss" src="../assets/css/main.scss"></style>
<script>
import Vue from "vue";
// import instanceFacetService from "utilities/instance-facets";
// import axios from 'axios'

export default Vue.component('facet-browser', {
    props: ['class-uri'],
    data: function() {
        return {
            isLoadingResults: false,

            scope: {
                type : "=",
                constraints : "=?",
                title : "=?",
                vizConfig: null,
            },
            transclude : true,
            restrict: "E",
            facetValues: null,
            facets: [
                {
                    name: 'test',
                    label: 'testlabel',
                    values: ['test1value','test1value2'],
                },
                {
                    name: 'test2',
                    label: 'testlabel2',
                    values: ['testvalue2']
                }
            ],
            facetName: "",

            dataConfig: {
                "url": null,
                // "baseurl" : ROOT_URL+'about?uri='+encodeURIComponent(scope.type)+"&view=instance_data",
            },

          vizConfig: {
            "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
            "data": {
              "values":[],
            },
            "view" : "instanceAttributes",
            "mark": "point",
            "autosize": {
                "type": "fit",
                "contains": "padding",
                "resize" : "true"
            },
            "encoding" : {},
            "width" : 1000,
            "height" : 700,
            "resize" : "true",
            "config": {
                "style": {
                    "guide-label" : {
                        "fontSize": 16
                    },
                    "guide-title" : {
                        "fontSize": 20
                    },
                    "label" : {
                        "fontSize": 14
                    },
                    "group-title" : {
                        "fontSize": 24
                    }
                }
            }
          }
        }
    },
    methods: {
      // Disable the facets while results are being retrieved.
      disableFacets() {
          return this.isLoadingResults;
      },
      // Setup the FacetHandler options.
      getFacetOptions() {
        var options = instanceFacets.getFacetOptions();
        options.scope = this.scope;

        // Get initial facet values from URL parameters (refresh/bookmark) using facetUrlStateHandlerService.
        options.initialState = facetUrlStateHandlerService.getFacetValuesFromUrlParams();
        return options;
      },
      updateResults(event, facetSelections) {
        console.log("Updating facet instance data.");
        this.scope.updatable = false;
        this.isLoadingResults = true;
        instanceFacets.getResults(facetSelections).then(function(pager) {
                            vm.pager = pager;
                            dataConfig.constraints = [];
                            if (facetSelections.constraint) {
                                dataConfig.constraints = facetSelections.constraint;
                            }

                            // this.scope.getFacetValues = instanceFacets.getFacetValues;

                            this.facetValues = [];
                            for (facetName in facetSelections.facets) {
                                if (facetSelections.facets[facetName].id) {
                                    facetSelections.facets[facetName].value.forEach(function(val) {
                                        if (val.field !== undefined) {
                                            this.facetValues.push(val);
                                            if (val.indep_vals !== undefined) {
                                                val.indep_vals.forEach(function (indep_val) {
                                                    indep_val.indep_val = true;
                                                    this.facetValues.push(indep_val);
                                                })
                                            }
                                        }

                                    });
                                }
                            }

                            scope.getFacetValues().forEach(function(facetValue) {
                                if (facetValue.value === undefined) {
                                    if (scope.includeFacetsAsCategory[facetValue.facetId]) {
                                        facetValue.selectionType = "Show";
                                        this.facetValues.push(facetValue);
                                    }
                                }
                            });

                                    //return true; // Include top level categories.
                            //    if (variable_names[facetValue.facetId] && variable_names[facetValue.facetId][facetValue.value])
                            //        return true;
                            //    else return false;
                            //});
                            //dataConfig.url = scope.spec.data.baseurl;
                            //dataConfig.url += '&variables='+encodeURIComponent(JSON.stringify(scope.facetValues));
                            //if (facetSelections.constraints) {
                            //    dataConfig.url += "&constraints="+encodeURIComponent(JSON.stringify(facetSelections.constraints));
                            //}
                            //console.log(scope.spec.data.url);
                            $http
                                .get(ROOT_URL+'about', {
                                    params: {
                                        uri: this.scope.type,
                                        view:'instance_data',
                                        constraints: JSON.stringify(facetSelections.constraint),
                                        variables: JSON.stringify(this.facetValues
                                            .filter(function(v) { return !v.indep_val}))
                                    },
                                    responseType:'text'
                                })
                                .then(function(response) {
                                    this.dataConfig.query = response.data;
                                    console.log("query", this.dataConfig.query)
                                    $http
                                        .get(ROOT_URL+'sparql', {params : {query : this.dataConfig.query, output: 'json'}, responseType: 'json'})
                                        .then(function(response) {
                                            this.vizConfig.data = { values: transformSparqlData(response.data) };
                                            this.scope.allData = this.vizConfig.data.values;
                                            this.facetValues.forEach(function(facetValue) {
                                                if (facetValue.type != "nominal") {
                                                    var extent = d3.extent(this.vizConfig.data.values,
                                                                           d => d[facetValue.field]);
                                                    facetValue.min = extent[0];
                                                    if (facetValue.lower === undefined) {
                                                        facetValue.lower = facetValue.min;
                                                    }
                                                    facetValue.max = extent[1];
                                                    if (facetValue.upper === undefined) {
                                                        facetValue.upper = facetValue.max;
                                                    }
                                                    console.log(facetValue);
                                                }
                                            })
                                            this.isLoadingResults = false;
                                        });
                                });

                        });
                    }

    },
    created: function () {
    }
});

</script>

<!--/*************************ORIGINAL ANGULAR FACETS CODE************************** */

<!--/*
     * The controller.
     */
    app.directive("instanceFacets", [
        'FacetHandler', 'instanceFacetService', "facetUrlStateHandlerService", 'getLabel', '$http', 'loadAttributes', 'transformSparqlData',
        function(FacetHandler, instanceFacetService, facetUrlStateHandlerService, getLabel, $http, loadAttributes, transformSparqlData) {
	    return {
                scope: {
                    type : "=",
                    constraints : "=?",
                    title : "=?"
                },
                transclude : true,
                templateUrl: ROOT_URL+'static/html/instanceFacets.html',
	        restrict: "E",
                link: function(scope, element, attrs) {
                    var vm = scope;

                    var updateId = 0;

                    var dataConfig = {
                        "url": null,
                        "baseurl" : ROOT_URL+'about?uri='+encodeURIComponent(scope.type)+"&view=instance_data",
                    };
                    scope.dataConfig = dataConfig;
                    scope.vizConfig = {
                        "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
                        "data": {
                        },
                        "view" : "instanceAttributes",
                        "mark": "point",
                        "autosize": {
                            "type": "fit",
                            "contains": "padding",
                            "resize" : "true"
                        },
                        "encoding" : {},
                        "width" : 1000,
                        "height" : 700,
                        "resize" : "true",
                        "config": {
                            "style": {
                                "guide-label" : {
                                    "fontSize": 16
                                },
                                "guide-title" : {
                                    "fontSize": 20
                                },
                                "label" : {
                                    "fontSize": 14
                                },
                                "group-title" : {
                                    "fontSize": 24
                                }
                            }
                        }
                    };

                    var instanceFacets = instanceFacetService(scope.type, scope.constraints);

                    // page is the current page of results.
                    vm.makeArray = makeArray;
                    vm.getLabel = getLabel;

                    vm.disableFacets = disableFacets;
                    scope.view = "help";
                    vm.updateResults = updateResults;

                    // Listen for the facet events
                    // This event is triggered when a facet's selection has changed.
                    scope.$on('sf-facet-constraints', function(event, cons) {
                        scope.cons = cons;
                        scope.updatable = true;
                    });
                    // This is the initial configuration event
                    var initListener = scope.$on('sf-initial-constraints', function(event, cons) {
                        scope.cons = cons;
                        updateResults(event, cons);
                        // Only listen once, then unregister
                        initListener();
                    });

                    // Get the facet configurations from dbpediaService.
                    vm.facets = instanceFacets.getFacets();
                    // Initialize the facet handler
                    vm.handler = new FacetHandler(getFacetOptions());


                    // Disable the facets while results are being retrieved.
                    function disableFacets() {
                        return vm.isLoadingResults;
                    }

                    // Setup the FacetHandler options.
                    function getFacetOptions() {
                        var options = instanceFacets.getFacetOptions();
                        options.scope = scope;

                        // Get initial facet values from URL parameters (refresh/bookmark) using facetUrlStateHandlerService.
                        options.initialState = facetUrlStateHandlerService.getFacetValuesFromUrlParams();
                        return options;
                    }

                    scope.includeFacetsAsCategory = {};

                    // Get results based on facet selections (each time the selections change).
                    function updateResults(event, facetSelections) {
                        console.log("Updating facet instance data.");
                        scope.updatable = false;
                        vm.isLoadingResults = true;
                        instanceFacets.getResults(facetSelections).then(function(pager) {
                            vm.pager = pager;
                            dataConfig.constraints = [];
                            if (facetSelections.constraint) {
                                dataConfig.constraints = facetSelections.constraint;
                            }

                            //var variable_names = {};
                            //for (facetName in facetSelections.facets) {
                            //    variable_names[facetName] = {};
                            //    if (facetSelections.facets[facetName].id) {
                            //        facetSelections.facets[facetName].value.forEach(function(val) {
                            //            variable_names[facetName][val.value.replace(/^<|>$/g,"")] = true;
                            //        });
                            //    }
                            //}

                            scope.getFacetValues = instanceFacets.getFacetValues;

                            scope.facetValues = [];
                            for (facetName in facetSelections.facets) {
                                if (facetSelections.facets[facetName].id) {
                                    facetSelections.facets[facetName].value.forEach(function(val) {
                                        if (val.field !== undefined) {
                                            scope.facetValues.push(val);
                                            if (val.indep_vals !== undefined) {
                                                val.indep_vals.forEach(function (indep_val) {
                                                    indep_val.indep_val = true;
                                                    scope.facetValues.push(indep_val);
                                                })
                                            }
                                        }

                                    });
                                }
                            }

                            scope.getFacetValues().forEach(function(facetValue) {
                                if (facetValue.value === undefined) {
                                    if (scope.includeFacetsAsCategory[facetValue.facetId]) {
                                        facetValue.selectionType = "Show";
                                        scope.facetValues.push(facetValue);
                                    }
                                }
                            });

                                    //return true; // Include top level categories.
                            //    if (variable_names[facetValue.facetId] && variable_names[facetValue.facetId][facetValue.value])
                            //        return true;
                            //    else return false;
                            //});
                            //dataConfig.url = scope.spec.data.baseurl;
                            //dataConfig.url += '&variables='+encodeURIComponent(JSON.stringify(scope.facetValues));
                            //if (facetSelections.constraints) {
                            //    dataConfig.url += "&constraints="+encodeURIComponent(JSON.stringify(facetSelections.constraints));
                            //}
                            //console.log(scope.spec.data.url);
                            $http
                                .get(ROOT_URL+'about', {
                                    params: {
                                        uri: scope.type,
                                        view:'instance_data',
                                        constraints: JSON.stringify(facetSelections.constraint),
                                        variables: JSON.stringify(scope.facetValues
                                            .filter(function(v) { return !v.indep_val}))
                                    },
                                    responseType:'text'
                                })
                                .then(function(response) {
                                    scope.dataConfig.query = response.data;
                                    console.log("query", scope.dataConfig.query)
                                    $http
                                        .get(ROOT_URL+'sparql', {params : {query : scope.dataConfig.query, output: 'json'}, responseType: 'json'})
                                        .then(function(response) {
                                            scope.vizConfig.data = { values: transformSparqlData(response.data) };
                                            scope.allData = scope.vizConfig.data.values;
                                            scope.facetValues.forEach(function(facetValue) {
                                                if (facetValue.type != "nominal") {
                                                    var extent = d3.extent(scope.vizConfig.data.values,
                                                                           d => d[facetValue.field]);
                                                    facetValue.min = extent[0];
                                                    if (facetValue.lower === undefined) {
                                                        facetValue.lower = facetValue.min;
                                                    }
                                                    facetValue.max = extent[1];
                                                    if (facetValue.upper === undefined) {
                                                        facetValue.upper = facetValue.max;
                                                    }
                                                    console.log(facetValue);
                                                }
                                            })
                                            vm.isLoadingResults = false;
                                        });
                                });

                        });
                    }
                    scope.updateResults = updateResults;

                    scope.updateFilters = function() {
                        if (scope.allData) {
                            scope.vizConfig.data = { values: scope.allData.filter(function(row) {
                                var include = true;
                                scope.facetValues.forEach(function(facetValue) {
                                    if (facetValue.min !== undefined) {
                                        if (row[facetValue.field] < facetValue.lower ||
                                            row[facetValue.field] > facetValue.upper) {
                                            include = false;
                                        }
                                    }
                                });
                                return include;
                            })};
                        }
                    };
                    scope.$watch(function(scope) {
                        if (scope.facetValues) {
                            return scope.facetValues.map(function(d) {
                                return {lower:d.lower, upper:d.upper};
                            });
                        } else return [];
                    },scope.updateFilters, true);

                    function makeArray(val) {
                        return angular.isArray(val) ? val : [val];
                    }

                }
            };
        }]);

    app.service("transformSparqlData", function() {
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

        return function (sparqlResults) {
            const data = []
            console.log("sparqlResults", sparqlResults)
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
        };
    })
