(function (angular) {

    var module = angular.module('jsonLdEditor', ['ngMaterial', 'ui.bootstrap']);

    module.directive("contenteditable", function() {
        return {
            restrict: "A",
            require: "ngModel",
            link: function(scope, element, attrs, ngModel) {
                
                function read() {
                    ngModel.$setViewValue(element.html());
                }
                
                ngModel.$render = function() {
                    element.html(ngModel.$viewValue || "");
                };
                
                element.bind("blur keyup change", function() {
                    scope.$apply(read);
                });
            }
        };
    });

    module.factory('context', ['$http', '$q', '$sce', function($http, $q, $sce) {
        var cache = {};
        function context(resource, parentContext) {
            var promise = $q.defer();
            if (!resource['@context']) promise.resolve(parentContext);
            else {
                context = resource['@context'];
                if (typeof context === 'string' || context instanceof String) {
                    if (cache[context]) {
                        return cache[context].promise;
                    } else {
                        cache[context] = promise;
                        $http.get(context, {responseType: 'json'})
                            .then(function(data, status, headers, config) {
                                var context = data.data;
                                if (context['@context']) context = context['@context'];
                                promise.resolve(Object.assign({}, parentContext, context));
                            });
                    }
                } else {
                    promise.resolve(Object.assign({}, parentContext, context));
                }
            }
            return promise.promise;
        }
        return context;
    }]);

    module.factory('datatypes', function() {
        var result = [
            'xsd:string',
            'xsd:boolean',
            'xsd:decimal',
            'xsd:float',
            'xsd:double',
            'xsd:duration',
            'xsd:dateTime',
            'xsd:time',
            'xsd:date',
            'xsd:gYearMonth',
            'xsd:gYear',
            'xsd:gMonthDay',
            'xsd:gDay',
            'xsd:gMonth',
            'xsd:hexBinary',
            'xsd:base64Binary',
            'xsd:anyURI'
        ];
        return result;
    });
    
    module.factory('contextualize',function() {
        function contextualize(uri, inverseContext) {
            var result = uri;
            if (inverseContext[result]) return inverseContext[result];
            var keys = [];
            for (key in inverseContext) {
                keys.push(key);
            }
            keys = keys.sort(function(a, b){
                // ASC  -> a.length - b.length
                // DESC -> b.length - a.length
                return b.length - a.length;
            });
            for (key in keys) {
                if (uri.startsWith(keys[key])) {
                    var replacement = inverseContext[keys[key]];
                    if (replacement == "@vocab") uri = uri.replace(keys[key], "");
                    else result = uri.replace(keys[key], replacement+":");
                    break;
                }
            }
            if (inverseContext[result]) result = inverseContext[result];
            return result;
        }
        return contextualize;
    });

    module.service("getView", [ '$http', '$q', function($http, $q) {
        var promises = {};
        function getView(uri, view, responseType) {
            if (!promises[uri]) promises[uri] = {};
            if (!promises[uri][view]) {
                promises[uri][view] = $q.defer();
                $http.get(ROOT_URL+'about',{ params: {uri:uri,view:view}, responseType:'json'})
                    .then(function(response) {
                        promises[uri][view].resolve(response.data);
                    });
            }
            return promises[uri][view].promise;
        };
        return getView;
    }]);

    module.service('resolveEntity', ["$http", function($http) {
        var promises = {};
        /**
         * Search for nodes.
         */
	    function resolveEntity (query) {
            if (!promises[query]) {
                promises[query] = $q.defer();
                $http.get('',{params: {view:'resolve',term:query+"*"}, responseType:'json'})
                    .then(function(response) {
                        promises[query].resolve(response.data.map(function(hit) {
                            hit.value = angular.lowercase(hit.label);
                            return hit;
                        }));
                    });
                return promises[query].promise;
            }
	    }
        return resolveEntity;
    }]);
    
    module.directive('jsonLdEditor', ['context', 'RecursionHelper', 'contextualize', "$mdMenu", 'datatypes', 'makeID','resolveEntity', '$mdToast',
                                      function(context, RecursionHelper, contextualize, $mdMenu, datatypes, makeID, resolveEntity, $mdToast) {
        return {
            templateUrl: ROOT_URL+"static/html/jsonLdEditor.html",
            restrict: 'EAC',
            scope: {
                resource: '=',
                parent: '=',
                property: '=',
                context: '=',
                index: "=",
                globalContext: '=',
                collapseAll: '='
            },
            compile: function(element) {
                return RecursionHelper.compile(element, function(scope) {
                    // when loading page
                    // collapse all after the policy type
                    scope.isCollapsed = null;
                    
                    if (scope.resource['@type'] && scope.resource['@type'][0] === "https://tw.rpi.edu/web/projects/DSA/xacml-core/Policy") {
                        scope.isCollapsed = false;
                    } else {
                        scope.isCollapsed = true;
                    }
                    
                    scope.collapseToggle = function() {
                        scope.isCollapsed = !scope.isCollapsed;
                    }

                    scope.$watch('collapseAll', function(){
                        console.log("running collapseAll function");
                        console.log("scope.collapseAll is:", scope.collapseAll)
                        if (scope.collapseAll === true) {
                            console.log("collapseAll is true")
                            if (scope.resource['@type'] && scope.resource['@type'][0] === "https://tw.rpi.edu/web/projects/DSA/xacml-core/Policy") {
                                scope.isCollapsed = false;
                            } else {
                                console.log("collapseAll is true")
                                scope.isCollapsed = true;
                            }
                        } else {
                            console.log("collapseAll is false")
                            scope.isCollapsed = false;
                        }
                    });

                    scope.openMenu = function(ev) {
                        originatorEv = ev;
                        $mdMenu.show(ev);
                    };
                    scope.$watch("context",function() {
                        context(scope.resource, scope.context)
                            .then(function(localContext) {
                                scope.localContext = localContext;
                                scope.inverseContext = {};
                                for (key in scope.localContext) {
                                    scope.inverseContext[scope.localContext[key]] = key;
                                }
                            });
                    });
                    scope.isArray = function(variable) {
                        if (variable === undefined || variable === null) return false;
                        if (typeof variable === 'string' || variable instanceof String) return false;
                        return typeof variable === 'Array' || variable instanceof Array || variable.constructor === Array;
                    };

                    scope.querySearch = function(text) {
                        console.log("querySearch text", text);
                        var results = [];
                        var resultMap = {};
                        [scope.context, scope.globalContext].forEach(function(A) {
                            for (var entry in A) {
                                if (entry.startsWith("$$")) continue;
                                if (entry.startsWith("@")) continue;

                                console.log(entry);
                                if (angular.lowercase(entry).indexOf(angular.lowercase(text)) != -1 && !resultMap[entry]) {
                                    resultMap[entry] = true;
                                    results.push(entry);
                                }
                            }
                        });
                        resolveEntity(text).then(function(hits) {
                            hits.forEach(function(d) {
                                if (!resultMap[d.node]) {
                                    resultMap[d.node] = true;
                                    results.push(d.node);
                                }
                            });
                        });
                        console.log(results);
                        return results;
                    };

                    scope.querySearchType = function(text) {
                        console.log("querySearch text", text);
                        var results = [];
                        var resultMap = {};

                        resultMap["Loading..."] = true;
                        results.push("Loading...");
                        
                        resolveEntity(text).then(function(hits) {
                            delete resultMap["Loading..."];
                            results.splice(0, 1);
                            hits.forEach(function(d) {
                                if (!resultMap[d.node]) {
                                    resultMap[d.node] = true;
                                    results.push(d.node);
                                    console.log("d.node", d.node);
                                }
                            });
                        });

                        console.log(results);
                        return results;
                    };

                    scope.querySearchID = function(text, type) {
                        console.log("querySearch text", text);
                        var results = [];
                        var resultMap = {};

                        resultMap["Loading..."] = true;
                        results.push("Loading...");
                        
                        resolveEntity(text, type).then(function(hits) {
                            delete resultMap["Loading..."];
                            results.splice(0, 1);
                            hits.forEach(function(d) {
                                if (!resultMap[d.node]) {
                                    resultMap[d.node] = true;
                                    results.push(d.node);
                                    console.log("d.node", d.node);
                                }
                            });
                        });

                        console.log(results);
                        return results;
                    };

                    function labelize(uri) {
                        if (uri == null || uri.length == 0) return uri;
                        var localPart = uri.split("#").filter(function(d) {return d.length > 0});
                        localPart = localPart[localPart.length-1];
                        localPart = localPart.split("/").filter(function(d) {return d.length > 0});
                        localPart = localPart[localPart.length-1];
                        localPart = localPart.replace("_"," ");
                        return decodeURIComponent(localPart);
                    }
                    
                    scope.getLabel = function(resource) {
                        if (scope.isArray(resource)) return null;
                        if (scope.isString(resource)) return labelize(resource);
                        var preferred = [
                            'http://www.w3.org/2000/01/rdf-schema#label',
                            'http://www.w3.org/2004/02/skos/core#preferredLabel',
                            'http://purl.org/dc/terms/title',
                            'http://purl.org/dc/elements/1.1/title',
                            'http://schema.org/name',
                            'http://xmlns.com/foaf/0.1/name',
                            'http://www.w3.org/2004/02/skos/core#altLabel',
                        ];
                        for (i in preferred) {
                            var uri = preferred[i];
                            var result = null;
                            if (resource[uri]) result = resource[uri];
                            if (result == null && scope.inverseContext) {
                                var contextualized = contextualize(uri, scope.inverseContext);
                                if (resource[contextualized]) result = resource[contextualized];
                            }
                            if (result != null) {
                                if (scope.isArray(result)) {
                                    if (result.length == 0) continue;
                                    result = result[0];
                                }
                                if (result['@value'] !== undefined) result = result['@value'];
                                return result;
                            }
                        }
                        return labelize(resource['@id']);
                    };
                    scope.isString = function(o) {
                        return typeof o === 'string' || o instanceof String;
                    };
                    scope.getID = function() {
                        if (scope.isString(scope.resource)) return scope.resource;
                        return scope.resource['@id'];
                    };
                    scope.isResourceProperty = function(property) {
                        if (property == "@type" || property == "@graph") return true;
                        if (scope.localContext && scope.localContext[property] && scope.localContext[property]['@type']) {
                            if (scope.localContext[property]['@type'] == '@id') return true;
                            if (scope.localContext[property]['@type'] == '@value') return false;
                        }
                        return null;
                    };
                    scope.isLiteralProperty = function(property) {
                        var propertyType = scope.isResourceProperty(property);
                        if (propertyType !== null) return !propertyType;
                        else return false;
                    };
                    scope.isResource = function(resource, property) {
                        if (property == null) {
                            return true;
                        }
                        var propertyType = scope.isResourceProperty(property);
                        if (propertyType !== null) return propertyType;
                        if (resource['@id'] || resource['@graph']) return true;
                        if (resource['@value']) return false;
                        return false;
                    }
                    scope.getProperties = function(resource) {
                        var properties = [];
                        if (typeof resource === 'string' || resource instanceof String) return [];
                        for (var property in resource) {
                            if (property.startsWith("$$")) continue;
                            if (property.startsWith("@")) continue;
                            if (resource.hasOwnProperty(property) && property != '@id' &&
                                property != '@graph' && property != "@context") {
                                    properties.push(property);
                                }
                        }
                        return properties;
                    };
                    scope.appendValue = function(resource, property, $event) {
                        console.log('appendvalue $event:', $event)
                        console.log("localContext at appendValue:", scope.localContext);
                        console.log("Property that we are constraining:", property);
                        console.log("Class that we are constraining(scope.resource['@type']):", scope.resource["@type"]);
                        if (scope.resource[property] === undefined || scope.resource[property] === null)
                            scope.addProperty(property);
                        if (!scope.isArray(scope.resource[property])) {
                            var existing = scope.resource[property];
                            scope.resource[property] = [existing];
                        }
                        console.log("typeof resource:",typeof resource);
                        if (typeof resource === 'object' && resource !== null) {
                            if (resource["@value"] === undefined) {
                                if (resource["@id"] === undefined || resource["@id"] === "") resource["@id"] = makeID();
                                if (resource["@type"] === undefined || resource["@type"] === "") resource["@type"] = "http://www.w3.org/2002/07/owl#Thing";
                            }
                        }
                        scope.resource[property].push(resource);
                        //get jquery lite event target to color 'tr' element
                        let targetEl = angular.element($event.target);
                        console.log('targetEl that I am putting into the validateEditor()', targetEl)
                        scope.validateEditor(scope.resource, property, targetEl);
                    };
                    scope.queryProperties = function(query) {
                        var list = [];
                        if (query) {
                            list.push({display:query, value: angular.lowercase(query)});
                        }
                        for (key in scope.localContext) {
                            if (!scope.resource[key]) {
                                list.push({display: key, value: angular.lowercase(key)});
                            }
                        }
                        function createFilterFor(query) {
                            var lowercaseQuery = angular.lowercase(query);
                            return function filterFn(property) {
                                return (property.value.indexOf(lowercaseQuery) === 0);
                            };
                        }
                        var results = query ? list.filter( createFilterFor(query) ) : list;
                        return results;
                    };
                    scope.queryDatatypes = function(query) {
                        var list = [query].concat(datatypes);
                        function createFilterFor(query) {
                            var lowercaseQuery = angular.lowercase(query);
                            return function filterFn(x) {
                                return (angular.lowercase(x).indexOf(lowercaseQuery) === 0);
                            };
                        }
                        var results = query ? list.filter( createFilterFor(query) ) : list;
                        return results;
                    };
                    //not being used
                    scope.queryDatatypeItems = function(query) {
                        var datatypes = scope.queryDatatypes(query);
                        var results = [];
                        for (datatype of datatypes) {
                            var item = {};
                            item["display"] = datatype;
                            item["value"] = scope.getFullUri(item.display);
                            results.push(item);
                        }
                        return results;
                    };
                    /*
                    scope.evaluateDatatype = function(resource, property, datatype) {
                        console.log("scope.evaluateDatatype property:", property);
                        console.log("scope.evaluateDatatype datatype:", datatype);
                        console.log("scope.evaluateDatatype scope.parent[@type]:", scope.parent["@type"]);
                        console.log("scope.evaluateDatatype scope.parent[property]:", scope.parent[property]);
                        console.log("scope.evaluateDatatype scope.globalContext[property]:", scope.globalContext[property]);
                        scope.validateEditor(scope.parent, scope.property);
                    };*/
                    scope.queryLanguages = function(query) {
                        var list = [query];
                        function createFilterFor(query) {
                            var lowercaseQuery = angular.lowercase(query);
                            return function filterFn(x) {
                                return (angular.lowercase(x).indexOf(lowercaseQuery) === 0);
                            };
                        }
                        var results = query ? list.filter( createFilterFor(query) ) : list;
                        return results;
                    };
                    scope.addProperty = function(property) {
                        if (property === undefined) return;
                        if (scope.isString(scope.resource)) {
                            var newResource = {"@id" : scope.resource};
                            if (scope.index !== undefined) scope.parent[scope.property][scope.index] = newResource;
                            else scope.parent[scope.property] = newResource;
                            scope.resource = newResource;
                        }
                        if (!scope.resource[property]) {
                            scope.resource[property] = [];
                        }
                        //scope.validateEditor(scope.parent, scope.property);
                    };
                    scope.addDatatype = function() {
                        if (scope.isString(scope.resource)) {
                            var newResource = {"@value" : scope.resource};
                            if (scope.index !== undefined) scope.parent[scope.property][scope.index] = newResource;
                            else scope.parent[scope.property] = newResource;
                            scope.resource = newResource;
                        }
                        scope.resource['@type'] = null;
                    };
                    scope.addLanguage = function() {
                        if (scope.isString(scope.resource)) {
                            var newResource = {"@value" : scope.resource};
                            if (scope.index !== undefined) scope.parent[scope.property][scope.index] = newResource;
                            else scope.parent[scope.property] = newResource;
                            scope.resource = newResource;
                        }
                        scope.resource['@language'] = null;
                    };
                    scope.isRemovable = function() {
                        return scope.parent != null && scope.property != null;
                    };

                    // add in $event!
                    scope.remove = function($event) {
                        //console.log("jsonLdEditor remove scope.globalContext:", scope.globalContext);
                        console.log('what is $event', $event);
                        //get event target jquery lite
                        let targetEl = angular.element($event.target);
                        console.log("jsonLdEditor remove scope.property:", scope.property);
                        console.log("jsonLdEditor remove scope.parent:", scope.parent);
                        console.log("jsonLdEditor remove scope.index:", scope.index);
                        if (scope.index !== undefined)
                            scope.parent[scope.property].splice(scope.index, 1);
                        else 
                            delete scope.parent[scope.property];
                        scope.validateEditor(scope.parent, scope.property, targetEl);
                    };
                    scope.validateEditor = function(resource, property, targetEl, eventTarget) {
                        //when md-autocomplete calls validateEditor, targetEl is not defined and can only pass event.target
                        if (!targetEl && eventTarget) {
                            targetEl = angular.element(eventTarget);
                            console.log("changing targetEl with eventTarget:", eventTarget)
                        }
                        // what is targetEl?
                        console.log("validateEditor targetEl is:", targetEl)
                        //what is color of background?
                        let backgroundColor = targetEl.closest('tr').css('background-color');
                        console.log('background-color is:', backgroundColor);
                        
                        //reset background color and delete alert
                        targetEl.closest('tr').css('background-color', 'rgb(255,255,255)');
                        targetEl.closest('tr').find('div.alert.alert-danger').remove();
                        console.log("jsonLdEditor validateEditor resource:", resource);
                        console.log("jsonLdEditor validateEditor property:", property);
                        let constraints = scope.retrieveConstraints(resource, property);
                        console.log("jsonLdEditor validateEditor constraints:", constraints);
                        var lengthObject = {};
                        for (assertion of resource[property]) {
                            //doesn't work except for has description:
                            //string is default type string if not set
                            // if (!assertion.hasOwnProperty('@type')) {assertion['@type'] = 'xsd:string'}

                            console.log("constraints[0]['@range']:", constraints[0]['@range']);
                            console.log('assertion:',assertion) //added {@type: []} to appendValue 
                            console.log("isArray(assertion['@type']) is:", scope.isArray(assertion['@type']));
                            //{ @type: [] } now will go thru after checking if it's an array.
                            //this if statement works with "has condition"                    do this first then check datatype
                            //checking @type for datatype (xsd:string) and doesn't have property
                            if (assertion["@type"] && (!scope.isArray(assertion['@type'])) && (constraints[0]['@propertyLabel'] !== property) ) { 
                                var datatypeUri = scope.getFullUri(assertion["@type"]);
                                console.log("datatypeUri", datatypeUri)
                                // check if the type matches the range then add up the number of times
                                if ( datatypeUri === constraints[0]['@range'] ) {
                                    if (lengthObject[datatypeUri]) {
                                        lengthObject[datatypeUri]++;
                                    } else {
                                        lengthObject[datatypeUri] = 1;
                                    }
                                }
                            //works for combining algorithm
                            //for has combining algorithm needs to check property label vs property then can create length obj (assertion['type']==="")    
                            } else if ( constraints[0]['@propertyLabel'] === property ) {
                                //adding up the lengthObject
                                ( lengthObject.hasOwnProperty(constraints[0]['@range']) ) ? lengthObject[constraints[0]['@range']]++ : lengthObject[constraints[0]['@range']] = 1;
                            }                 
                            
                        }
                        console.log("scope.validateEditor lengthObject:", lengthObject);

                        for (constraint of constraints) {
                            console.log("scope.validateEditor constraint['@extent']:", constraint["@extent"]);
                            console.log("scope.validateEditor constraint['@range']:", constraint["@range"]);
                            console.log("scope.validateEditor constraint['@cardinality']:", constraint["@cardinality"]);
                            //console.log("scope.validateEditor lengthObject[constraint['@range']]:", lengthObject[constraint["@range"]]);
                            if (!lengthObject[constraint["@range"]]) lengthObject[constraint["@range"]] = 0;
                            
                            //must have 1 or more
                            if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#someValuesFrom") {
                                if (lengthObject[constraint["@range"]] < 1) {
                                    console.log("scope.validateEditor [WARNING 1]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                    let warningDialog1 = `Must have exactly 1 or more of ${constraint["@propertyLabel"]}`
                                    scope.showHideToast(warningDialog1);
                                    console.log('Warning 1, lengthObject is:', lengthObject);
                                    console.log('Warning 1 property is:', property);

                                    //background color yellow for rowif it's not meeting this constraint
                                    targetEl.closest('tr').css('background-color','lightyellow');
                                    //warning dialog also!
                                    targetEl.closest('tr').find('json-ld-editor').first().append(`
                                        <div layout="row" layout-align="space-between center" class="alert alert-danger" ng-show="showAlert">
                                            <span>${warningDialog1}</span>
                                        </div>
                                    `);

                                }
                                //must have the number specified in cardinality (no more no less)
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#qualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] != constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING 2]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                    let warningDialog2 = `Must have exactly ${constraint['@cardinality']} ${constraint["@propertyLabel"]}`;
                                    scope.showHideToast(warningDialog2);
                                    console.log('Warning 2, lengthObject is:', lengthObject);
                                    console.log('Warning 2 property is:', property)
                                    
                                    //background color yellow for row if it's not meeting this constraint
                                    let closest = targetEl.closest('tr');
                                    console.log('closest is: ', closest);
                                    console.log('targetEl.closest("tr").find("json-ld-editor").first() is:', targetEl.closest('tr').find('json-ld-editor').first() );
                                    closest.css('background-color','lightyellow');
                                    targetEl.closest('tr').find('json-ld-editor').first().append(`
                                        <div layout="row" layout-align="space-between center" class="alert alert-danger" ng-show="showAlert">
                                            <span>${warningDialog2}</span>
                                        </div>
                                    `);
                                                    // <md-button ng-click="showAlert = !showAlert">
                                                    //     <md-icon class="material-icons md-48">clear</md-icon>
                                                    // </md-button>


                                }
                                //must have at least the number that's in cardinality 
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#minQualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] < constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING 3]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                    let warningDialog3 = `Doesn't satisfy minimum amount for "${constraint['@propertyLabel']}"`;
                                    targetEl.closest('tr').css('background-color', 'lightyellow');
                                    scope.showHideToast(warningDialog3);
                                    targetEl.closest('tr').find('json-ld-editor').first().append(`
                                        <div layout="row" layout-align="space-between center" class="alert alert-danger" ng-show="showAlert">
                                            <span>${warningDialog3}</span>
                                        </div>
                                    `);
                                }
                                //must have no more than this amount
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#maxQualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] > constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING 4]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                    let warningDialog4 = `Gone over maximum (${constraint["@cardinality"]}) for "${constraint['@propertyLabel']}"`;
                                    targetEl.closest('tr').css('background-color', 'lightyellow');
                                    scope.showHideToast(warningDialog4);
                                    targetEl.closest('tr').find('json-ld-editor').first().append(`
                                        <div layout="row" layout-align="space-between center" class="alert alert-danger" ng-show="showAlert">
                                            <span>${warningDialog4}</span>
                                        </div>
                                    `);
                                }
                            }
                            //constraint["@extent"]
                            //constraint["@cardinality"]
                            //constraint["@range"]
                            //resource[property]
                        }
                    };

                    //toast
                    scope.showHideToast = function (message) {
                        $mdToast.show({
                                        // template  : `<md-toast id="toast-container"><span flex>${message}</span><md-button ng-click="closeToast()">X</md-button></md-toast>`,
                                        template  : `<md-toast id="toast-container"><span flex>${message}</span><md-button ng-click="closeToast()"><md-icon class="material-icons md-48" style="color:#d4d5db !important;">clear</md-icon></md-button></md-toast>`,
                                        hideDelay : 5000,
                                        parent    : angular.element(document.getElementById('toast-container')),
                                        controller: "toastController",
                                      });
                    }
                    scope.showDialog = function(){
                        //put more info here from toast or chip
                    }

                    scope.getFullUri = function(prefixedUri) {
                        let uriRegEx = /^(http|https)/i
                        if (uriRegEx.test(prefixedUri)) {
                            console.log("scope.getFullUri already a full URI:", prefixedUri);
                            return prefixedUri;
                        } else {
                            console.log("scope.getFullUri a prefixed URI:", prefixedUri);
                        }
                        var prefixes = {
                            'xsd':'http://www.w3.org/2001/XMLSchema#',
                            'dc':'http://purl.org/dc/elements/1.1/',
                            'dct':'http://purl.org/dc/terms/',
                            'rdfs':'http://www.w3.org/2000/01/rdf-schema#'
                        };
                        let regexBeginning = /.+?(?=:)/g
                        let regexEnd = /[^:]+$/g
                        let suffix = prefixedUri.match(regexEnd);
                        let prefix = prefixedUri.match(regexBeginning);
                        console.log("suffix is:",suffix);
                        console.log("prefix is:",prefix);
                        if (prefix === null) {
                            console.log("no matches for prefix in getFullUri");
                            return prefixedUri;
                        } else {
                            return prefixes[prefix[0]] + suffix[0];
                        }
                    };
                    scope.retrieveConstraints = function(resource, property) {
                        let constraints = [];
                        console.log("inside retrieveContstraints resource:",resource);
                        console.log("inside retrieveContstraints property:",property);
                        console.log("inside retrieveContstraints scope.globalContext:",scope.globalContext);
                        if (property == '@type') {
                            console.log(scope.$parent)
                            property = scope.$parent.$parent.$parent.property
                            console.log("retrieve constraints new property:", property)
                            for (constraint of scope.globalContext[property]){
                                if (resource["@type"] && constraint["@class"] === resource["@type"]) {
                                    console.log("constraint pushed", constraint);
                                    constraints.push(constraint);
                                }
                            }
                            return constraints;
                        }
                        for (constraint of scope.globalContext[property]) {
                            if (resource["@type"] && constraint["@class"] === resource["@type"][0]) {
                                console.log("constraint pushed", constraint);
                                constraints.push(constraint);
                            }
                        }
                        return constraints;
                    }
                });
            }
        };
    }]);

    module.controller('toastController', function($scope, $mdToast){
        $scope.closeToast = function(){
            $mdToast.hide()
        }    
    })

    module.factory('RecursionHelper', ['$compile', function($compile){
        return {
            /**
             * Manually compiles the element, fixing the recursion loop.
             * @param element
             * @param [link] A post-link function, or an object with function(s) registered via pre and post properties.
             * @returns An object containing the linking functions.
             */
            compile: function(element, link){
                // Normalize the link parameter
                if(angular.isFunction(link)){
                    link = { post: link };
                }
                
                // Break the recursion loop by removing the contents
                var contents = element.contents().remove();
                var compiledContents;
                return {
                    pre: (link && link.pre) ? link.pre : null,
                    /**
                     * Compiles and re-adds the contents
                     */
                    post: function(scope, element){
                        // Compile the contents
                        if(!compiledContents){
                            compiledContents = $compile(contents);
                        }
                        // Re-add the compiled contents to the element
                        compiledContents(scope, function(clone){
                            element.append(clone);
                        });
                        
                        // Call the post-linking function, if any
                        if(link && link.post){
                            link.post.apply(null, arguments);
                        }
                    }
                };
            }
        };
    }]);

    
})(angular);
