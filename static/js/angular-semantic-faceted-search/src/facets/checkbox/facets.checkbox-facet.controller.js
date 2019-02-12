(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('CheckboxFacetController', CheckboxFacetController);

    /* ngInject */
    function CheckboxFacetController($scope, $controller, CheckboxFacet) {
        var args = { $scope: $scope, FacetImpl: CheckboxFacet };
        return $controller('AbstractFacetController', args);
    }
})();
