/* eslint-env jasmine */
/* global inject, module */

describe('FacetHandler', function() {
    var $rootScope, scope, FacetHandler, options;

    beforeEach(module('seco.facetedSearch'));
    beforeEach(inject(function(_FacetHandler_, _$rootScope_) {
        $rootScope = _$rootScope_;
        FacetHandler = _FacetHandler_;
        scope = $rootScope.$new();
        spyOn(scope, '$broadcast');

        options = {
            scope: scope,
            rdfClass: '<http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord>',
            constraint: '?id skos:prefLabel ?name .',
            preferredLang : 'fi'
        };

    }));

    it('should broadcast constraints at init', function() {
        var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
        var data = { facets: {}, constraint: cons, config: options };
        new FacetHandler(options);
        expect(scope.$broadcast).toHaveBeenCalledWith('sf-initial-constraints', data);
    });

    it('should broadcast initial constraints when requested', function() {
        var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
        var data = { facets: {}, constraint: cons, config: options };
        new FacetHandler(options);

        scope.$broadcast.calls.reset();

        scope.$emit('sf-request-constraints');

        expect(scope.$broadcast).toHaveBeenCalledWith('sf-initial-constraints', data);
    });

    it('should listen for facet changes and broadcast constraints', function() {
        new FacetHandler(options);

        var args = {
            id: 'facetId',
            constraint: '?id <pred> <obj> .',
            value: '<obj>'
        };
        scope.$emit('sf-facet-changed', args);

        var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
        var updatedCons = [args.constraint].concat(cons);

        var data = { facets: { facetId: args }, constraint: updatedCons };

        expect(scope.$broadcast).toHaveBeenCalledWith('sf-facet-constraints', data);
    });

    it('should sort the constraints by priority when broadcasting', function() {
        new FacetHandler(options);

        var args1 = {
            id: 'f1',
            constraint: '?id <1> <obj> .',
            value: '<obj>'
        };
        scope.$emit('sf-facet-changed', args1);

        var args2 = {
            id: 'f2',
            constraint: '?id <2> <obj> .',
            value: '<obj>',
            priority: 1
        };
        scope.$emit('sf-facet-changed', args2);

        scope.$broadcast.calls.reset();

        var args3 = {
            id: 'f3',
            constraint: '?id <3> <obj> .',
            value: '<obj>',
            priority: 10
        };
        scope.$emit('sf-facet-changed', args3);

        var updatedCons = [
            '?id <2> <obj> .',
            '?id <3> <obj> .',
            '?id <1> <obj> .',
            ' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'
        ];

        var data = {
            facets: {
                f1: args1,
                f2: args2,
                f3: args3
            },
            constraint: updatedCons
        };

        expect(scope.$broadcast).toHaveBeenCalledWith('sf-facet-constraints', data);
    });
});
