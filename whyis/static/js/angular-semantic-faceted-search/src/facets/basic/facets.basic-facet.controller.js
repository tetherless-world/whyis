(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('BasicFacetController', BasicFacetController);

    /* ngInject */
    function BasicFacetController($scope, $controller, BasicFacet) {
        var args = { $scope: $scope, FacetImpl: BasicFacet };
        return $controller('AbstractFacetController', args);
    }
})();
