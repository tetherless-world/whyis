(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('AbstractFacetController', AbstractFacetController);

    /* @ngInject */
    function AbstractFacetController($scope, $log, _, EVENT_FACET_CONSTRAINTS,
            EVENT_FACET_CHANGED, EVENT_REQUEST_CONSTRAINTS, EVENT_INITIAL_CONSTRAINTS,
            FacetImpl) {

        var vm = this;

        vm.isLoading = isLoading;
        vm.changed = changed;

        vm.disableFacet = disableFacet;
        vm.enableFacet = enableFacet;

        vm.getFacetSize = getFacetSize;

        vm.listener = function() { };

        vm.getSpinnerKey = getSpinnerKey;

        // Wait until the options attribute has been set.
        var watcher = $scope.$watch('options', function(val) {
            if (val) {
                init(FacetImpl);
                watcher();
            }
        });

        function init(Facet) {
            var initListener = $scope.$on(EVENT_INITIAL_CONSTRAINTS, function(event, cons) {
                var opts = _.cloneDeep($scope.options);
                opts = angular.extend({}, cons.config, opts);
                opts.initial = cons.facets;
                vm.facet = new Facet(opts);
                if (vm.facet.isEnabled()) {
                    vm.previousVal = _.cloneDeep(vm.facet.getSelectedValue());
                    listen();
                    update(cons);
                }
                // Unregister initListener
                initListener();
            });
            $scope.$emit(EVENT_REQUEST_CONSTRAINTS);
        }

        var spinnerKey;
        function getSpinnerKey() {
            if (!spinnerKey) {
                spinnerKey = _.uniqueId('spinner');
            }
            return spinnerKey;
        }

        function listen() {
            vm.listener = $scope.$on(EVENT_FACET_CONSTRAINTS, function(event, cons) {
                update(cons);
            });
        }

        function update(constraints) {
            vm.isLoadingFacet = true;
            return vm.facet.update(constraints).then(handleUpdateSuccess, handleError);
        }

        function isLoading() {
            return vm.isLoadingFacet || !vm.facet || vm.facet.isLoading();
        }

        function emitChange(forced) {
            var val = vm.facet.getSelectedValue();
            if (!forced && _.isEqual(vm.previousVal, val)) {
                vm.isLoadingFacet = false;
                return;
            }
            vm.previousVal = _.cloneDeep(val);
            var args = {
                id: vm.facet.facetId,
                constraint: vm.facet.getConstraint(),
                value: val
            };
            $scope.$emit(EVENT_FACET_CHANGED, args);
        }

        function changed() {
            vm.isLoadingFacet = true;
            emitChange();
        }

        function enableFacet() {
            listen();
            vm.isLoadingFacet = true;
            vm.facet.enable();
            emitChange(true);
        }

        function disableFacet() {
            vm.listener();
            vm.facet.disable();
            var forced = vm.facet.getSelectedValue() ? true : false;
            emitChange(forced);
        }

        function handleUpdateSuccess() {
            vm.error = undefined;
            vm.isLoadingFacet = false;
        }

        function handleError(error) {
            if (!vm.facet.hasError()) {
                $log.info(error);
                // The facet has recovered from the error.
                // This happens when an update has been cancelled
                // due to changes in facet selections.
                return;
            }
            $log.error(error);
            vm.isLoadingFacet = false;
            if (error) {
                vm.error = error;
            } else {
                vm.error = 'Error';
            }
        }

        function getFacetSize(facetStates) {
            if (facetStates) {
                return Math.min(facetStates.length + 2, 10).toString();
            }
            return '10';
        }
    }
})();
