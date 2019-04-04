NG_DOCS={
  "sections": {
    "api": "API Documentation"
  },
  "pages": [
    {
      "section": "api",
      "id": "index",
      "shortName": "index",
      "type": "overview",
      "moduleName": "index",
      "shortDescription": "SPARQL Faceter - Client-Side Faceted Search Using SPARQL",
      "keywords": "$on $scope ammatti api argument ascending attribute based basic better birth birthmunicipality birthplace box broadcasting broadcasts built-in caching change changes cidoc-crm classes client-side collection common configuration configured constraint constraints controller custom data-options dataservice death deathdate default define defined defines directive directives displayed documentation easily emits emitted enabled endpointurl endpredicate equalto event events facet faceted facetedsearch faceter facethandler facetid facets facetstate false fetches fi fields filtering free-text friendly function generated getresults handler handles hierarchical hierarchy http implemented individual init initial initialize initlistener interested jena key labels listen listening listens maintaining max mediates min module municipality muninn-project narrows objectfollowing occupation optimize options order org overview path pattern predicate preferredlang preflabel presumably principalabode priority profession property query range rank rdfclass reasonably responsible resultset scope search seco secobasicfacet secohierarchyfacet secojenatextfacet secotextfacet secotimespanfacet select selections service services set setup sf-facet-constraints sf-facets-changed sf-initial-constraints skos sorts source sparql startpredicate support synchronizes template text time title triple true types undefined unique update updateresults updates usable users values var variable vm w3 work works",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch",
      "shortName": "seco.facetedSearch",
      "type": "overview",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "SPARQL Faceter - Client-Side Faceted Search Using SPARQL",
      "keywords": "api client-side faceted facetedsearch faceter main module overview search seco sparql",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoBasicFacet",
      "shortName": "secoBasicFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A basic select box facet with text filtering.",
      "keywords": "additional api basic bound box button case chart clicking config configuration constraint currently default define defined defines directive disabled display displayed en enable enabled endpoint endpoints example facet facetedsearch facethandler facets filtering friendly generate generated globally headers helpful http kinds label labels language languages list multiple note object optional options order org pattern patterns people pie predicate preferred priority properties property query rdfs resource restriction retrieve seco select selectable selection separate service services set skos sorting sparql specifier structure subjects supported tag text title triple truthy undefined unique uri uris url usable users values variable",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoCheckboxFacet",
      "shortName": "secoCheckboxFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A facet for a checkbox selector based on a triple pattern.",
      "keywords": "additional api based bound button chart checkbox checkboxes choice choices clicking config configuration constraint create default definitions directive disabled display displayed element enable enabled endpoint example facet facetedsearch facethandler facets friendly globally headers hobby http label list multiple object optional options org pattern pie priority property resource resources restrict result seco selected selections selector set sorting sparql structure title triple truthy undefined union unique uniqueidforthischoice url usable users values variable",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoFacetWrapper",
      "shortName": "secoFacetWrapper",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "Wraps facets in a shared template.",
      "keywords": "api directive facetedsearch facets seco shared template wraps",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoHierarchyFacet",
      "shortName": "secoHierarchyFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A select box facet for hierarchical values.",
      "keywords": "additional api bound box case config configuration constraint default define defined defines depth directive disabled displayed en enabled endpoint example facet facetedsearch facethandler facets friendly generated globally headers helpful hierarchical hierarchy http kinds label labels language languages list maximum multiple object optional options order org path pattern people predicate preferred priority properties property rdfs resource restriction seco select selectable selection set skos sorting sparql specifier structure subjects supported tag title triple undefined unique uri url usable users values variable",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoJenaTextFacet",
      "shortName": "secoJenaTextFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A free-text search facet using Jena text search.",
      "keywords": "apache api avoid backend backslashes based captured case changed character configuration consecutive constraint continue default defined directive disabled displayed documentation enabled endpoint errors escaped facet facetedsearch facets free-text friendly generates graph html include jena left limit modified number object odd option options order org parentheses patterns predicate priority produced property queries query query-with-sparql quotes reflected removed sanitization sanitized score search seco set sort sorting sparql structure supports syntax terms text time title tokens triggers triple typed undefined unique uri usable user users valid variable word wrapped writing wrote",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoTextFacet",
      "shortName": "secoTextFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A free-text search facet.",
      "keywords": "api configuration constraint default defines directive disabled displayed enabled facet facetedsearch facets free-text friendly generates object options path patterns predicate priority property queries search seco set sorting sparql structure text title triple typed undefined unique usable users values variable",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.directive:secoTimespanFacet",
      "shortName": "secoTimespanFacet",
      "type": "directive",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "A facet for selecting date ranges.",
      "keywords": "additional api based config configuration constraint currently data dates default defines directive disabled discarded displayed earliest enabled endpoint facet facetedsearch facethandler facets format friendly globally headers http iso issues lead maximum minimum object optional options org path predefined predicate priority property range ranges restricts retrieved seco selectable selecting selections set sorting sparql start string structure support supports timezone timezones title type undefined underlying unique url usable user users values variable w3",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.FacetHandler",
      "shortName": "seco.facetedSearch.FacetHandler",
      "type": "function",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "Service for mediating the communication between facets.",
      "keywords": "$rootscope additional api argument array broadcast broadcasting broadcasts built-in case collection communication config configuration constants constraint constraints created default defined directly emitted en endpoint event event_facet_changed event_facet_constraints event_initial_constraints event_request_constraints events example extra facet faceted facetedsearch facethandler facetid facets faceturlstatehandlerservice fields function generated headers http included individual individually init initial injectable instantiating key labels language languages listeners listening listens loading mediating method names needed object omitting optional order parameters parent pattern preferred properties rdf reason remove removelisteners resource resources response scope seco selects service sf-facet-changed sf-facet-constraints sf-facets-changed sf-initial-constraints sf-request-constraints shorthand sparql structure tag triple url values",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.FacetHandler",
      "shortName": "seco.facetedSearch.FacetHandler",
      "type": "object",
      "moduleName": "seco.facetedSearch",
      "keywords": "api facetedsearch facethandler object seco",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.FacetResultHandler",
      "shortName": "seco.facetedSearch.FacetResultHandler",
      "type": "object",
      "moduleName": "seco.facetedSearch",
      "keywords": "api facetedsearch facetresulthandler object seco",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.FacetResultHandler",
      "shortName": "seco.facetedSearch.FacetResultHandler",
      "type": "function",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "Service for retrieving SPARQL results based on facet selections.",
      "keywords": "advancedsparqlservice angular-paging-sparql-service api based best block broadcast comparators configuration constraint default defined en endpoint endpointconfig example facet facetedsearch facethandler facetresulthandler facets facetselections filter function getresults github http https included insure io mapper method number object objectmapperservice optional options order package paged paging parameter placeholder prefixes properties query querytemplate rdf rdfs reflect required resources restrict result resultoptions retrieve retrieving seco select selections service skos sort sorting sparql template true truthy url variable variables wrap",
      "isDeprecated": false
    },
    {
      "section": "api",
      "id": "seco.facetedSearch.facetUrlStateHandlerService",
      "shortName": "seco.facetedSearch.facetUrlStateHandlerService",
      "type": "service",
      "moduleName": "seco.facetedSearch",
      "shortDescription": "facetUrlStateHandlerService",
      "keywords": "api based bookmarking broadcast configuration current details events facet facetedsearch facethandler facets faceturlstatehandlerservice getfacetvaluesfromurlparams initialstate intended listening method parameters received retrieving return seco selections service update updates updateurlparams updating url values",
      "isDeprecated": false
    }
  ],
  "apis": {
    "api": true
  },
  "html5Mode": false,
  "editExample": true,
  "startPage": "/api",
  "scripts": [
    "angular.min.js"
  ]
};