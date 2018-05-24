(function (angular) {

    var module = angular.module('jsonLdEditor', [
         'ngMaterial'
    ]);

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

    module.directive('jsonLdEditor', ['context', 'RecursionHelper', 'contextualize', "$mdMenu", 'datatypes', 'makeID',
                                      function(context, RecursionHelper, contextualize, $mdMenu, datatypes, makeID) {
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
            },
            // controller: function($scope) {
            //     console.log("jsonLdEditor-controller:", $scope.globalContext);
            // },
            compile: function(element) {
                return RecursionHelper.compile(element, function(scope) {
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
                    scope.appendValue = function(resource, property) {
                        console.log("localContext at appendValue:", scope.localContext);
                        console.log("Property that we are constraining:", property);
                        console.log("Class that we are constraining:", scope.resource["@type"]);
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
                        scope.validateEditor(scope.resource, property);
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
                    scope.remove = function() {
                        //console.log("jsonLdEditor remove scope.globalContext:", scope.globalContext);
                        //console.log("jsonLdEditor remove scope.property:", scope.property);
                        //console.log("jsonLdEditor remove scope.parent:", scope.parent);
                        if (scope.index !== undefined)
                            scope.parent[scope.property].splice(scope.index, 1);
                        else 
                            delete scope.parent[scope.property];
                        scope.validateEditor(scope.parent, scope.property);
                    };
                    scope.validateEditor = function(resource, property) {
                        console.log("jsonLdEditor validateEditor resource:", resource);
                        console.log("jsonLdEditor validateEditor property:", property);
                        let constraints = scope.retrieveConstraints(resource, property);
                        console.log("jsonLdEditor validateEditor constraints:", constraints);
                        var lengthObject = {};
                        for (assertion of resource[property]) {
                            if (assertion["@type"]) {
                                var datatypeUri = scope.getFullUri(assertion["@type"]);
                                if (lengthObject[datatypeUri]) {
                                    lengthObject[datatypeUri]++;
                                } else {
                                    lengthObject[datatypeUri] = 1;
                                }
                            }
                        }
                        console.log("scope.validateEditor lengthObject:", lengthObject);
                        for (constraint of constraints) {
                            console.log("scope.validateEditor constraint['@extent']:", constraint["@extent"]);
                            console.log("scope.validateEditor constraint['@range']:", constraint["@range"]);
                            console.log("scope.validateEditor constraint['@cardinality']:", constraint["@cardinality"]);
                            //console.log("scope.validateEditor lengthObject[constraint['@range']]:", lengthObject[constraint["@range"]]);
                            if (!lengthObject[constraint["@range"]]) lengthObject[constraint["@range"]] = 0;
                            if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#someValuesFrom") {
                                if (lengthObject[constraint["@range"]] < 1) {
                                    console.log("scope.validateEditor [WARNING]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                }
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#qualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] != constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                }
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#minQualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] < constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                }
                            } else if (constraint["@extent"] === "http://www.w3.org/2002/07/owl#maxQualifiedCardinality") {
                                if (lengthObject[constraint["@range"]] > constraint["@cardinality"]) {
                                    console.log("scope.validateEditor [WARNING]: " + constraint["@class"] + "---" + constraint["@extent"] + "---" + constraint["@range"] + "--- NOT SATISFIED");
                                }
                            }
                            //constraint["@extent"]
                            //constraint["@cardinality"]
                            //constraint["@range"]
                            //resource[property]
                        }
                    };
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
                        if (prefix === null) {
                            console.log("no matches for prefix in getFullUri");
                            return prefixedUri;
                        } else {
                            return prefixes[prefix[0]] + suffix[0];
                        }
                    };
                    scope.retrieveConstraints = function(resource, property) {
                        let constraints = [];
                        for (constraint of scope.globalContext[property]) {
                            if (resource["@type"] && constraint["@class"] === resource["@type"][0]) {
                                console.log("constraint pushed");
                                constraints.push(constraint);
                            }
                        }
                        return constraints;
                    }
                });
            }
        };
    }]);

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
