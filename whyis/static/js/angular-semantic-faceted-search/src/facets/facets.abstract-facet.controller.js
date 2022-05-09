(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .controller('AbstractFacetController', AbstractFacetController);

    /* @ngInject */
    function AbstractFacetController($scope, $log, _, EVENT_FACET_CONSTRAINTS,
            EVENT_FACET_CHANGED, EVENT_REQUEST_CONSTRAINTS, EVENT_INITIAL_CONSTRAINTS,
            FacetChartService, FacetImpl) {

        var vm = this;

        vm.isLoading = isLoading;
        vm.isChartVisible = isChartVisible;
        vm.hasChartButton = hasChartButton;

        vm.changed = changed;

        vm.toggleFacetEnabled = toggleFacetEnabled;
        vm.disableFacet = disableFacet;
        vm.enableFacet = enableFacet;
        vm.toggleChart = toggleChart;

        vm.getFacetSize = getFacetSize;

        vm.initOptions = initOptions;
        vm.init = init;
        vm.listener = function() { };
        vm.listen = listen;
        vm.update = update;
        vm.emitChange = emitChange;
        vm.handleUpdateSuccess = handleUpdateSuccess;
        vm.handleError = handleError;
        vm.handleChartClick = handleChartClick;
        vm.updateChartData = updateChartData;

        vm.getSpinnerKey = getSpinnerKey;

        // Wait until the options attribute has been set.
        var watcher = $scope.$watch('options', function(val) {
            if (val) {
                vm.init();
                watcher();
            }
        });

        function init() {
            var initListener = $scope.$on(EVENT_INITIAL_CONSTRAINTS, function(event, cons) {
                vm.initOptions(cons);
                // Unregister initListener
                initListener();
            });
            $scope.$emit(EVENT_REQUEST_CONSTRAINTS);
        }

        function initOptions(cons) {
            cons = cons || {};
            var opts = _.cloneDeep($scope.options);
            opts = angular.extend({}, cons.config, opts);
            opts.initial = cons.facets;
            vm.facet = vm.facet || new FacetImpl(opts);
            if (vm.facet.isEnabled()) {
                vm.previousVal = _.cloneDeep(vm.facet.getSelectedValue());
                vm.listen();
                vm.update(cons);
            }
            if (opts.chart) {
                vm.chart = vm.chart || new FacetChartService({ facet: vm.facet, scope: $scope });
            }
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
                vm.update(cons);
            });
        }

        function update(constraints) {
            vm.isLoadingFacet = true;
            return vm.facet.update(constraints).then(vm.handleUpdateSuccess, handleError);
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
                value: val,
                priority: vm.facet.getPriority()
            };
            $scope.$emit(EVENT_FACET_CHANGED, args);
        }

        function changed() {
            vm.isLoadingFacet = true;
            vm.emitChange();
        }

        function toggleFacetEnabled() {
            vm.facet.isEnabled() ? vm.disableFacet() : vm.enableFacet();
        }

        function enableFacet() {
            vm.listen();
            vm.isLoadingFacet = true;
            vm.facet.enable();
            vm.init();
        }

        function disableFacet() {
            if (vm.listener) {
                vm.listener();
            }
            vm.facet.disable();
            var forced = vm.facet.getSelectedValue() ? true : false;
            vm.emitChange(forced);
        }

        function handleUpdateSuccess() {
            vm.updateChartData();
            vm.error = undefined;
            vm.isLoadingFacet = false;
        }

        function toggleChart() {
            vm._showChart = !vm._showChart;
        }

        function isChartVisible() {
            return vm._showChart;
        }

        function hasChartButton() {
            return vm.facet.isEnabled() && !!vm.chart;
        }

        function updateChartData() {
            if (vm.chart) {
                return vm.chart.updateChartData();
            }
        }

        function handleChartClick(chartElement) {
            vm.chart.handleChartClick(chartElement);
            return vm.changed();
        }

        function handleError(error) {
            if (!vm.facet.hasError()) {
                $log.info(error);
                // The facet has recovered from the error.
                // This happens when an update has been cancelled
                // due to changes in facet selections.
                return;
            }
            $log.error(error.statusText || error);
            vm.isLoadingFacet = false;
            vm.error = 'Error' + (error.status ? ' (' + error.status + ')' : '');
        }

        function getFacetSize(facetStates) {
            if (facetStates) {
                return Math.min(facetStates.length + 2, 10).toString();
            }
            return '10';
        }
    }
})();
