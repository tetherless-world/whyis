/* eslint-env jasmine */
/* global inject, module  */
describe('BasicFacetController', function() {
    beforeEach(module('seco.facetedSearch'));

    var $q, $controller, $rootScope, $scope, initial, controller,
        selectedValue;

    beforeEach(module(function($provide) {
        selectedValue = '<uri>';

        function MockConstructor() {
            var enabled = true;
            return {
                getSelectedValue: function() { return selectedValue; },
                getConstraint: function() { return 'constraint'; },
                getPriority: function() { return 1; },
                facetId: 'basicId',
                enable: function() { enabled = true; },
                update: function() { return $q.when(); },
                disable: function() { enabled = false; },
                isEnabled: function() { return enabled; }
            };
        }

        $provide.value('BasicFacet', MockConstructor);
    }));

    beforeEach(inject(function(_$controller_, _$rootScope_, _$q_){
        $rootScope = _$rootScope_;
        $controller = _$controller_;
        $scope = $rootScope.$new();
        $q = _$q_;

        initial = {
            config: {
                scope: $scope,
                constraint: ['default', 'constraint'],
                preferredLang : 'fi'
            }
        };
    }));

    beforeEach(function() {
        $scope.options = {};
        controller = $controller('BasicFacetController', { $scope: $scope });
        $scope.$digest();
        $scope.$broadcast('sf-initial-constraints', initial);
    });

    it('should listen for initial values initially', function() {
        spyOn($scope, '$emit');

        $scope.options = {};

        $controller('BasicFacetController', { $scope: $scope });
        $scope.$digest();

        expect($scope.$emit).toHaveBeenCalledWith('sf-request-constraints');
    });

    describe('vm.changed', function() {
        it('should emit the state of the facet if the state has changed', function() {
            spyOn($scope, '$emit');

            selectedValue = '<otherUri>';

            controller.changed();

            var args = { id: 'basicId', constraint: 'constraint', value: '<otherUri>', priority: 1 };
            expect($scope.$emit).toHaveBeenCalledWith('sf-facet-changed', args);
        });

        it('should not emit the state of the facet if the state has not changed', function() {
            spyOn($scope, '$emit');

            controller.changed();

            expect($scope.$emit).not.toHaveBeenCalled();
        });
    });

    describe('vm.enableFacet', function() {
        it('should enable facet, and emit a change event', function() {
            spyOn($scope, '$emit');
            spyOn(controller.facet, 'enable');

            controller.enableFacet();

            expect(controller.facet.enable).toHaveBeenCalled();
            expect($scope.$emit).toHaveBeenCalledWith('sf-request-constraints');
        });
    });

    describe('vm.disableFacet', function() {
        it('should disable facet, and emit a change event', function() {
            spyOn($scope, '$emit');
            spyOn(controller.facet, 'disable');

            controller.disableFacet();

            expect(controller.facet.disable).toHaveBeenCalled();
            expect($scope.$emit).toHaveBeenCalledWith('sf-facet-changed', jasmine.any(Object));
        });
    });

    describe('vm.hasChartButton', function() {
        it('should be true if facet is enabled and the option is enabled', function() {
            expect(controller.hasChartButton()).toBe(false);

            controller.disableFacet();
            expect(controller.hasChartButton()).toBe(false);

            controller.enableFacet();
            expect(controller.hasChartButton()).toBe(false);

            $scope.options.chart = true;
            controller.initOptions();
            expect(controller.hasChartButton()).toBe(true);
        });
    });
});
