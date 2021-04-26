(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoHierarchyFacet
    * @restrict 'E'
    * @element ANY
    * @description
    * A select box facet for hierarchical values.
    *
    * @param {Object} options The configuration object with the following structure:
    * - **facetId** - `{string}` - A friendly id for the facet.
    *   Should be unique in the set of facets, and should be usable as a SPARQL variable.
    * - **predicate** - `{string}` - The predicate or property path that defines the facet values.
    * - **hierarchy** - `{string}` - The predicate or property path that defines the hierarchy of values.
    * - **classes** - `{Array}` - The top level resources (URIs) of the hierarchy.
    * - **name** - `{string}` - The title of the facet. Will be displayed to end users.
    * - **[enabled]** `{boolean}` - Whether or not the facet is enabled by default.
    *   If undefined, the facet will be disabled by default.
    * - **[endpointUrl]** `{string}` - The URL of the SPARQL endpoint.
    *   Optional, as it can also be given globally in
    *   {@link seco.facetedSearch.FacetHandler `FacetHandler`} config.
    * - **[preferredLang]** - `{string|Array}` - The language tag that is preferred
    *   when getting labels for facet values, in case the value is a resource.
    *   The default is 'en'.
    *   Can also be a list of languages, in which case the languages are tried
    *   in order.
    *   If a label is not found in the given languages, a label without a
    *   language tag is used. If a label is still not found,
    *   the end part of the resource URI is used.
    *   Supported label properties are `skos:prefLabel`, and `rdfs:label`.
    * - **[priority]** - `{number}` - Priority for constraint sorting.
    *   Undefined by default.
    */
    angular.module('seco.facetedSearch')
    .directive('secoHierarchyFacet', hierarchyFacet);

    function hierarchyFacet() {
        return {
            restrict: 'E',
            scope: {
                options: '='
            },
            controller: 'HierarchyFacetController',
            controllerAs: 'vm',
            templateUrl: 'src/facets/basic/facets.basic-facet.directive.html'
        };
    }
})();
