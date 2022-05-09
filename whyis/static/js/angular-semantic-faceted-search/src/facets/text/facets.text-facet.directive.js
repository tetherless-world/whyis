(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoTextFacet
    * @restrict 'E'
    * @element ANY
    * @description
    * A free-text search facet.
    *
    * Does not make any SPARQL queries, just generates SPARQL triple patterns
    * out of the typed text for other facets to use.
    *
    * @param {Object} options The configuration object with the following structure:
    * - **facetId** - `{string}` - A friendly id for the facet.
    *   Should be unique in the set of facets, and should be usable as a SPARQL variable.
    * - **predicate** - `{string}` - The predicate or property path that defines the facet values.
    * - **name** - `{string}` - The title of the facet. Will be displayed to end users.
    * - **[enabled]** `{boolean}` - Whether or not the facet is enabled by default.
    *   If undefined, the facet will be disabled by default.
    * - **[priority]** - `{number}` - Priority for constraint sorting.
    *   Undefined by default.
    */
    angular.module('seco.facetedSearch')
    .directive('secoTextFacet', textFacet);

    function textFacet() {
        return {
            restrict: 'E',
            scope: {
                options: '='
            },
            controller: 'TextFacetController',
            controllerAs: 'vm',
            templateUrl: 'src/facets/text/facets.text-facet.directive.html'
        };
    }
})();
