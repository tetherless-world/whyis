(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('HierarchyFacetController', HierarchyFacetController);

    /* ngInject */
    function HierarchyFacetController($scope, $controller, HierarchyFacet) {
        var args = { $scope: $scope, FacetImpl: HierarchyFacet };
        return $controller('AbstractFacetController', args);
    }
})();
