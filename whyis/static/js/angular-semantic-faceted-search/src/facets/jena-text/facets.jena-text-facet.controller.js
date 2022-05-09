(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('JenaTextFacetController', JenaTextFacetController);

    /* ngInject */
    function JenaTextFacetController($controller, $scope, JenaTextFacet) {
        var args = { $scope: $scope, TextFacet: JenaTextFacet };
        return $controller('TextFacetController', args);
    }
})();
