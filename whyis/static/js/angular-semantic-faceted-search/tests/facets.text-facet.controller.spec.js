/* eslint-env jasmine */
/* global inject, module  */
describe('TextFacetController', function() {
    beforeEach(module('seco.facetedSearch'));

    var $controller, $rootScope, $q, $scope, mock, initial, controller, value;

    beforeEach(module(function($provide) {
        value = 'text';
        mock = {
            getSelectedValue: function() { return value; },
            getConstraint: function() { return 'constraint'; },
            getPriority: function() { return 1; },
            facetId: 'textId',
            clear: function() { value = undefined; },
            update: function() { return $q.when(); },
            enable: function() { },
            disable: function() { },
            isEnabled: function() { return true; }
        };
        var mockConstructor = function() { return mock; };

        $provide.value('TextFacet', mockConstructor);
    }));

    beforeEach(inject(function(_$controller_, _$rootScope_, _$q_){
        $rootScope = _$rootScope_;
        $controller = _$controller_;
        $q = _$q_;
        $scope = $rootScope.$new();

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
        controller = $controller('TextFacetController', { $scope: $scope });
        $scope.$digest();
        $scope.$broadcast('sf-initial-constraints', initial);
    });

    it('should listen for initial values initially', function() {
        spyOn($scope, '$emit');

        $scope.options = {};

        $controller('TextFacetController', { $scope: $scope });
        $scope.$digest();

        expect($scope.$emit).toHaveBeenCalledWith('sf-request-constraints');
    });

    describe('vm.changed', function() {
        it('should emit the state of the facet', function() {
            spyOn($scope, '$emit');

            value = 'new text';

            controller.changed();

            var args = { id: 'textId', constraint: 'constraint', value: value, priority: 1 };
            expect($scope.$emit).toHaveBeenCalledWith('sf-facet-changed', args);
        });
    });

    describe('vm.clear', function() {
        it('should call facet.clear, and emit change event', function() {
            spyOn($scope, '$emit');
            spyOn(controller.facet, 'clear').and.callThrough();

            controller.clear();

            expect(controller.facet.clear).toHaveBeenCalled();
            expect($scope.$emit).toHaveBeenCalledWith('sf-facet-changed', jasmine.any(Object));
        });
    });

    describe('vm.enableFacet', function() {
        it('should enable facet, and not emit a change event', function() {
            spyOn($scope, '$emit');
            spyOn(controller.facet, 'enable');

            controller.enableFacet();

            expect(controller.facet.enable).toHaveBeenCalled();
            expect($scope.$emit).not.toHaveBeenCalled();
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
});
