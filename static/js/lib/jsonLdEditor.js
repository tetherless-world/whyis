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

/*
    var editor_template = `
<md-card data-ng-if="!isArray(resource) && isResource(resource, property)">
  <md-card-title layout="row">
    <div flex="none">
      <div class="btn-group">
        <md-button class="md-icon-button" aria-label="Actions" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <md-icon class="material-icons md-light md-48">more_vert</md-icon>
        </md-button>
        <ul class="dropdown-menu">
          <li><a aria-label="Add Type" data-ng-click="appendValue({'@id':''},'@type'); ">
              <md-icon class="material-icons md-light md-48">add</md-icon>Add Type
          </a></li>
          <li><a aria-label="Remove" data-ng-click="remove()">
              <md-icon class="material-icons md-light md-48">clear</md-icon>Remove
          </a></li>
          <li><a aria-label="Add Named Graph" data-ng-click="addProperty('@graph')">
              <md-icon class="material-icons md-light md-48">group_work</md-icon>Add Named Graph
          </a></li>
          <li><a aria-label="Set Context..." data-ng-click="">
              <md-icon class="material-icons md-light md-48">label</md-icon>Set Context...
          </a></li>
        </ul>
      </div>
    </div>
    <md-card-title-text flex="auto">
      <span class="md-headline" ng-hide="getLabel(resource) == getID()">{{getLabel(resource)}} </span>
      <md-input-container class="md-subhead" md-no-float>
        <input placeholder="IRI" type="text" data-ng-if="index === undefined && isString(resource)" data-ng-model="parent[property]"></input>
        <input  placeholder="IRI" type="text"  data-ng-if="index !== undefined && isString(resource)" data-ng-model="parent[property][index]"></input>
        <input  placeholder="IRI" type="text"  data-ng-if="!isString(resource)" data-ng-model="resource['@id']"></input>
      </md-input-container>
    </md-card-title-text>
  </md-card-title>
  <md-card-content layout="column">
    <table width="100%" flex="100">
      <tr ng-if="resource['@type'] !== undefined" >
        <th style="vertical-align:top; padding: 8px;">type</th>
        <td width="100%">
          <json-ld-editor ng-if="resource['@type'] !== undefined" resource="resource['@type']" property="'@type'" parent="resource" context="localContext"/>
        </td>
        <td style="vertical-align:top">
          <md-button class="md-icon-button" aria-label="Add" ng-click="appendValue({'@value':''}, '@type')">
            <md-icon class="material-icons md-light md-48">add</md-icon>
          </md-button>
        </td>
      </tr>
      <tr data-ng-repeat="property in getProperties(resource)">
        <!-- th  style="vertical-align:top ; padding: 8px;">{{property}}</th -->
        <th  style="vertical-align:top ; padding: 8px;">{{resource[property]['@propertyLabel']}}</th>
        <td width="100%">
          <!-- json-ld-editor resource="resource[property]" property="property" parent="resource" context="localContext"/ -->
          <json-ld-editor resource="resource[property]" property="property['@propertyLabel']" parent="resource" context="localContext"/>
        </td>
        <td style="vertical-align:top">
          <div class="btn-group">
            <md-button class="md-icon-button" aria-label="Add" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <md-icon class="material-icons md-light md-48">add</md-icon>
            </md-button>
            <ul class="dropdown-menu dropdown-menu-right">
              <!-- li><a aria-label="Add a thing" ng-if="!isLiteralProperty(property)" ng-click="appendValue({'@id':''}, property)">Add a thing</a></li -->
              <!-- li><a aria-label="Add a value" ng-if="!isResourceProperty(property)" ng-click="appendValue({'@value':''}, property)">Add a value</a></li -->
              <!-- li><a aria-label="Add a thing" ng-if="!isLiteralProperty(Object.keys(property)[0])" ng-click="appendValue({'@id':''}, Object.keys(property)[0])">Add a thing</a></li -->
              <!-- li><a aria-label="Add a value" ng-if="!isResourceProperty(Object.keys(property)[0])" ng-click="appendValue({'@value':'','@propertyLabel':property['@propertyLabel'],'@key':property['@key']}, property['@key'])">Add a value</a></li -->
              <li><a aria-label="Add a thing" ng-if="!isLiteralProperty(property)" ng-click="appendValue({'@id':''}, Object.keys(property)[0])">Add a thing</a></li>
              <li><a aria-label="Add a value" ng-if="!isResourceProperty(Obproperty)" ng-click="appendValue({'@value':'','@propertyLabel':resource[property]['@propertyLabel'],'@key':resource[property]['@key']}, resource[property]['@key'])">Add a value</a></li>
            </ul>
          </div>
        </td>
      </tr>
      <tr>
        <td style="vertical-align:top; padding: 8px;">
          <md-autocomplete 
             md-selected-item="selectedProperty"
             md-search-text="searchProperty"
             md-selected-item-change="addProperty(item.display) ; searchProperty = selectedProperty = null"
             md-items="item in queryProperties(searchProperty)"
             md-autoselect="true"
             md-item-text="item.display"
             md-min-length="0"
             md-floating-label="+">
            <md-item-template>
              <span md-highlight-text="searchProperty" md-highlight-flags="^i">{{item.display}}</span>
            </md-item-template>
            <md-not-found>
              <a ng-click="addProperty(searchProperty) ; searchProperty = selectedProperty = null">Add Property <i>{{searchText}}</i></a>
            </md-not-found>
          </md-autocomplete>
        </td>
        <td width="100%">
        </td>
      </tr>
    </table>
    <md-content data-ng-if="resource['@graph']">
      <md-toolbar class="md-theme-light">
        <div class="md-toolbar-tools">
          <h2 flex md-truncate>Graph</h2>
          <md-button class="md-icon-button" aria-label="Add" ng-click="appendValue({'@id':''}, '@graph')">
            <md-icon class="material-icons md-light md-48">add</md-icon>
          </md-button>
        </div>
      </md-toolbar>
      <json-ld-editor resource="resource['@graph']" property="'@graph'" parent="resource" context="localContext"/>
    </md-content>
  </md-card-content>
</md-card>
<md-card flex="grow" layout="row" data-ng-if="!isArray(resource) && !isResource(resource, property)">
  <md-card-title>
    <div flex="none">
      <div class="btn-group">
        <md-button class="md-icon-button" aria-label="Actions" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <md-icon class="material-icons md-light md-48">more_vert</md-icon>
        </md-button>
        <ul class="dropdown-menu">
          <li><a aria-label="Remove" data-ng-click="remove()">
              <md-icon class="material-icons md-light md-48">clear</md-icon>Remove
          </a></li>
          <li><a disabled="{{resource['@type'] !== undefined}}" aria-label="Add Datatype" data-ng-click="addDatatype()">
              <md-icon class="material-icons md-light md-48">code</md-icon>Set Datatype...
          </a></li>
          <li><a disabled="{{resource['@language'] !== undefined}}" aria-label="Set Language" data-ng-click="addLanguage()">
              <md-icon class="material-icons md-light md-48">language</md-icon>Set Language...
          </a></li>
        </ul>
      </div>
    </div>
    <md-card-title-text layout="row">
      <md-input-container flex="grow" data-ng-show="resource['@value'] !== undefined" md-no-float >
        <textarea placeholder="Value" aria-label="{{property}}" rows="1" data-ng-model="resource['@value']"></textarea>
      </md-input-container>
      <md-input-container flex="grow" data-ng-show="index !== undefined && resource['@value'] === undefined" md-no-float>
        <textarea placeholder="Value" aria-label="{{property}}" rows="1" data-ng-model="parent[property][index]"></textarea>
      </md-input-container>
      <md-input-container flex="grow" data-ng-show="index === undefined && resource['@value'] === undefined" md-no-float>
        <textarea placeholder="Value" aria-label="{{property}}" rows="1"  data-ng-model="parent[property]"></textarea>
      </md-input-container>
      <md-autocomplete
         ng-if="resource['@type'] !== undefined"
         flex="initial"
         md-selected-item="resource['@type']"
         md-search-text="typeSearch"
         md-items="item in queryDatatypes(typeSearch)"
         md-autoselect="true"
         md-item-text="item"
         md-min-length="0"
         md-floating-label="Type">
        <md-item-template>
          <span md-highlight-text="typeSearch" md-highlight-flags="^i">{{item}}</span>
        </md-item-template>
        <md-not-found>
          <a ng-click="resource['@type'] = typeSearch">Add Datatype <i>{{typeSearch}}</i></a>
        </md-not-found>
      </md-autocomplete>
      <md-autocomplete
         ng-if="resource['@language'] !== undefined"
         flex="initial"
         md-selected-item="resource['@language']"
         md-search-text="searchLang"
         md-items="item in queryLanguages(searchLang)"
         md-autoselect="true"
         md-item-text="item"
         md-min-length="0"
         md-floating-label="Language">
        <md-item-template>
          <span md-highlight-text="searchLang" md-highlight-flags="^i">{{item}}</span>
        </md-item-template>
        <md-not-found>
          <a ng-click="resource['@language'] = searchLang">Add Language <i>{{searchLang}}</i></a>
        </md-not-found>
      </md-autocomplete>
  </md-card-title-text>
</md-card>
<div data-ng-if="isArray(resource)" layout="{{'column' ? parent === undefined : 'row'}}"  layout-wrap="true">
  <json-ld-editor flex="initial" data-ng-repeat="r in resource" resource="r" index="$index" property="property" parent="parent" context="localContext"></jsonLdEditor>
<md-button data-ng-if="parent == null" class="md-icon-button" aria-label="Add Thing">
  <md-icon class="material-icons md-light md-48">add</md-icon>
</md-button>
</div>
<style>
  json-ld-editor .well {
    margin-bottom: 0px;
  }
  json-ld-editor .panel-group {
    margin-bottom: 0px;
  }

  .md-errors-spacer {
    display: none;
  }
md-input-container {
    margin-bottom: 0px;
  }
  json-ld-editor md-card-title {
  padding: 4px;
  padding-top: 10px;
  }
  md-input-container {
  margin-top: 8px;
  }
  json-ld-editor md-card-content {
  padding-bottom: 8px;
  }
  json-ld-editor md-autocomplete {
  min-width: 100px;
  }
</style>
`
*/    
    module.directive('jsonLdEditor', ['context', 'RecursionHelper', 'contextualize', "$mdMenu", 'datatypes',
                                      function(context, RecursionHelper, contextualize, $mdMenu, datatypes) {
        return {
            templateUrl: ROOT_URL+"static/html/jsonLdEditor.html",
            restrict: 'EAC',
            scope: {
                resource: '=',
                parent: '=',
                property: '=',
                context: '=',
                index: "=",
            },
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
                                //console.log(uri, contextualized, resource[contextualized]);
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
                        console.log("isResource resource: ", resource);
                        console.log("isResource property: ", property);
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
                        //console.log("resource in getProperties: ", resource);
                        var properties = [];
                        if (typeof resource === 'string' || resource instanceof String) return [];
                        for (var property in resource) {
                            if (property.startsWith("$$")) continue;
                            if (property.startsWith("@")) continue;
                            if (resource.hasOwnProperty(property) && property != '@id' &&
                                property != '@graph' && property != "@context") {
                                    //console.log("property Key: ", property);
                                    properties.push(property);
                                    /*
                                    if (scope.isArray(resource[property])) {
                                        console.log("!!! this is an array: ", resource[property][0]);
                                        properties.push(resource[property][0]["@key"]);
                                    } else {
                                        console.log("!!! this is NOT an array: ", resource[property]);
                                        properties.push(resource[property]);
                                    }
                                    */
                                }
                        }
                        return properties;
                    };
                    scope.appendValue = function(resource, property) {
                        //console.log("!!! property: ", property);
                        //console.log("!!! resource: ", resource);
                        //console.log("!!! scope.resource[property]: ", scope.resource[property]);
                        if (scope.resource[property] === undefined || scope.resource[property] === null)
                            scope.addProperty(property);
                        if (!scope.isArray(scope.resource[property])) {
                            var existing = scope.resource[property];
                            scope.resource[property] = [existing];
                        }
                        scope.resource[property].push(resource);
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
                            //scope.resource[property] = [];
                            scope.resource[property] = {"@propertyLabel" : property};
                        }
                        
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
                        if (scope.index !== undefined)
                            scope.parent[scope.property].splice(scope.index, 1);
                        else 
                            delete scope.parent[scope.property];
                    };
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
