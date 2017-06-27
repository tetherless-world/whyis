(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('TimespanFacetController', TimespanFacetController);

    /* ngInject */
    function TimespanFacetController($scope, $controller, TimespanFacet) {
        var args = { $scope: $scope, FacetImpl: TimespanFacet };
        return $controller('AbstractFacetController', args);
    }
})();
