(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoFacetWrapper
    * @restrict 'E'
    * @element ANY
    * @description
    * Wraps facets in a shared template.
    */
    angular.module('seco.facetedSearch')
    .directive('secoFacetWrapper', facetWrapper);

    function facetWrapper() {
        return {
            restrict: 'E',
            transclude: true,
            templateUrl: 'src/facets/facets.facet-wrapper.directive.html'
        };
    }
})();
