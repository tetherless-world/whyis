(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('TextFacetController', TextFacetController);

    /* ngInject */
    function TextFacetController($scope, $controller, TextFacet) {
        var args = { $scope: $scope, FacetImpl: TextFacet };
        var vm = $controller('AbstractFacetController', args);

        vm.listen = function() { };
        vm.listener = function() { };

        vm.changed = changed;
        vm.clear = clear;
        vm.enableFacet = enableFacet;
        vm.isLoadingFacet = false;

        return vm;

        function changed() {
            vm.emitChange();
        }

        function clear() {
            vm.facet.clear();
            vm.emitChange();
        }

        function enableFacet() {
            vm.facet.enable();
        }
    }
})();
