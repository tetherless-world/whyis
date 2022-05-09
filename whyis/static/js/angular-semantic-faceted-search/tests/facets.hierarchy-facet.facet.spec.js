/* eslint-env jasmine */
/* global inject, module  */

describe('HierarchyFacet', function() {
    var $rootScope, $q, $timeout, mock, mockConstructor, HierarchyFacet, facet,
        options, natResponse, genResponse;

    beforeEach(module('seco.facetedSearch'));

    beforeEach(module(function($provide) {
        mock = { getObjectsNoGrouping: getResponse };
        mockConstructor = function() { return mock; };

        $provide.value('AdvancedSparqlService', mockConstructor);
    }));

    beforeEach(inject(function(){
        spyOn(mock, 'getObjectsNoGrouping').and.callThrough();
    }));

    beforeEach(inject(function(_$timeout_, _$q_, _$rootScope_, _HierarchyFacet_) {
        $timeout = _$timeout_;
        $q = _$q_;
        $rootScope = _$rootScope_;
        HierarchyFacet = _HierarchyFacet_;

        options = {
            endpointUrl: 'endpoint',
            name: 'Name',
            facetId: 'textId',
            predicate: '<pred>',
            hierarchy: '<hierarchy>',
            classes: ['<class1>', '<class2>'],
            enabled: true,
            depth: 3
        };

        facet = new HierarchyFacet(options);

        // These are the same as the ones in BasicFacet tests, but in this regard
        // the facets work the exact same way.
        genResponse = [
            {
                'value': undefined,
                'text': '-- No Selection --',
                'count': 94696
            },
            {
                'value': '<http://ldf.fi/narc-menehtyneet1939-45/sukupuoli/Mies>',
                'text': 'Mies',
                'count': 94286
            },
            {
                'value': '<http://ldf.fi/narc-menehtyneet1939-45/sukupuoli/Nainen>',
                'text': 'Nainen',
                'count': 405
            },
            {
                'value': '<http://ldf.fi/narc-menehtyneet1939-45/sukupuoli/Tuntematon>',
                'text': 'Tuntematon',
                'count': 5
            }
        ];

        natResponse = [
            {
                value: undefined,
                text: '-- No Selection --',
                count: 5
            },
            {
                value: '<http://ldf.fi/narc-menehtyneet1939-45/kansalaisuus/Ruotsi>',
                text: 'Ruotsi',
                count: 1
            },
            {
                value: '<http://ldf.fi/narc-menehtyneet1939-45/kansalaisuus/Suomi>',
                text: 'Suomi',
                count: 4
            }
        ];


    }));

    it('should be enabled if config says so', function() {
        expect(facet.isEnabled()).toBe(true);
    });

    it('should be disabled if config says so', function() {
        options.enabled = false;
        facet = new HierarchyFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should take its initial value from the config if present', function() {
        var iv = 'initial text';
        options.initial = { 'textId': { value: iv } };
        facet = new HierarchyFacet(options);

        expect(facet.getSelectedValue()).toEqual(iv);
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new HierarchyFacet(options);

            expect(facet.isEnabled()).toBe(false);

            facet.enable();

            expect(facet.isEnabled()).toBe(true);
        });
    });

    describe('disable', function() {
        it('should disable the facet', function() {
            facet.disable();

            expect(facet.isEnabled()).toBe(false);
        });
    });

    describe('getSelectedValue', function() {
        it('should get the selected value', function() {
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.selectedValue = { value: '<obj>' };

            expect(facet.getSelectedValue()).toEqual('<obj>');
        });
    });

    describe('getConstraint', function() {
        it('should return a constraint based on the selected value', function() {
            facet.selectedValue = { value: '<obj>' };

            var expected =
            ' ?seco_v_textId (<hierarchy>)* <obj> . ?id <pred> ?seco_v_textId . ';

            expect(facet.getConstraint().replace(/\s+/g, ' ')).toEqual(expected.replace(/\s+/g, ' '));

            facet.selectedValue = undefined;

            expect(facet.getConstraint()).toBeUndefined();
        });
    });

    describe('buildQuery', function() {
        it('should build a valid query', function() {
            var cons = ['?id <p> <o> .'];

            var expected =
            ' PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' +
            ' PREFIX skos: <http://www.w3.org/2004/02/skos/core#> ' +
            ' PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ' +
            ' SELECT DISTINCT ?cnt ?facet_text ?value WHERE {' +
            ' { ' +
            '  { ' +
            '   SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) { ' +
            '    ?id <p> <o> . ' +
            '   } ' +
            '  } ' +
            '  BIND("-- No Selection --" AS ?facet_text) ' +
            ' } UNION ' +
            '  {' +
            '   SELECT DISTINCT ?cnt ?value ?facet_text {' +
            '    {' +
            '     SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) ?value ?hierarchy ?lvl {' +
            '      { SELECT DISTINCT ?h { [] <pred> ?h . } } ' +
            '      ?h (<hierarchy>)* ?value . ' +
            '      OPTIONAL { ' +
            '       ?value <hierarchy> ?u0 . ?u0 <hierarchy> ?u1 . ?u1 <hierarchy> ?u2 . ' +
            '       BIND(CONCAT(STR(?u2),STR(?u1),STR(?u0),STR(?value)) AS ?_h) ' +
            '       BIND("--- " AS ?lvl) ' +
            '      } ' +
            '      OPTIONAL { ' +
            '       ?value <hierarchy> ?u0 . ?u0 <hierarchy> ?u1 . ' +
            '       BIND(CONCAT(STR(?u1),STR(?u0),STR(?value)) AS ?_h) ' +
            '       BIND("-- " AS ?lvl) ' +
            '      } ' +
            '      OPTIONAL { ' +
            '       ?value <hierarchy> ?u0 . ' +
            '       BIND(CONCAT(STR(?u0),STR(?value)) AS ?_h) ' +
            '       BIND("- " AS ?lvl) ' +
            '      } ' +
            '      OPTIONAL { BIND("" AS ?lvl) } ' +
            '      BIND(COALESCE(?_h, STR(?value)) AS ?hierarchy) ' +
            '      ?id <pred> ?h .' +
            '      ?id <p> <o> . ' +
            '     } GROUP BY ?hierarchy ?value ?lvl ORDER BY ?hierarchy ' +
            '    } ' +
            '    FILTER(BOUND(?value))' +
            '    BIND(COALESCE(?value, <http://ldf.fi/NONEXISTENT_URI>) AS ?labelValue) ' +
            '    OPTIONAL {' +
            '     ?labelValue skos:prefLabel ?lbl . ' +
            '     FILTER(langMatches(lang(?lbl), "fi")) .' +
            '    }' +
            '    OPTIONAL {' +
            '     ?labelValue rdfs:label ?lbl . ' +
            '     FILTER(langMatches(lang(?lbl), "fi")) .' +
            '    }' +
            '    OPTIONAL {' +
            '     ?labelValue skos:prefLabel ?lbl . ' +
            '     FILTER(langMatches(lang(?lbl), "")) .' +
            '    }' +
            '    OPTIONAL {' +
            '     ?labelValue rdfs:label ?lbl . ' +
            '     FILTER(langMatches(lang(?lbl), "")) .' +
            '    } ' +
            '    BIND(COALESCE(?lbl, STR(?value)) as ?label) ' +
            '    BIND(CONCAT(?lvl, ?label) as ?facet_text)' +
            '   }' +
            '  } ' +
            ' } ';
            expect(facet.buildQuery(cons).replace(/\s+/g, ' ')).toEqual(expected.replace(/\s+/g, ' '));
        });
    });


    describe('update', function() {
        it('should update the facet state according to query results', function() {
            var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
            var data = { facets: {}, constraint: cons };

            var qryRes;

            mock.response = natResponse;

            facet.update(data).then(function(res) {
                qryRes = res;
            });

            expect(mock.getObjectsNoGrouping).toHaveBeenCalled();

            $rootScope.$apply();

            expect(qryRes).toEqual(natResponse);
        });

        it('should not fetch results if facet is disabled', function() {
            var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
            var data = { facets: {}, constraint: cons };

            var qryRes;

            facet.disable();

            facet.update(data).then(function(res) {
                qryRes = res;
            });
            $rootScope.$apply();

            expect(qryRes).toBeUndefined();
            expect(mock.getObjectsNoGrouping).not.toHaveBeenCalled();
        });

        it('should abort if it is called again with different constraints', function() {
            var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
            var data = { facets: {}, constraint: cons };

            var qryRes;

            mock.wait = true;
            mock.response = natResponse;

            facet.update(data).then(function() {
                throw Error;
            }, function(error) {
                expect(error).toEqual('Facet state changed');
            });

            mock.wait = false;
            mock.response = genResponse;

            var newCons = ['?id ?p ?o .'];
            var newData = { facets: {}, constraint: newCons };

            facet.update(newData).then(function(res) {
                qryRes = res;
            });

            $rootScope.$apply();

            $timeout.flush();

            expect(qryRes).toEqual(genResponse);
        });

        it('should make the facet busy', function() {
            var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
            var data = { facets: {}, constraint: cons };
            mock.response = natResponse;

            expect(facet.isLoading()).toBeFalsy();

            facet.update(data);

            expect(facet.isLoading()).toBe(true);

            $rootScope.$apply();

            expect(facet.isLoading()).toBe(false);
        });
    });

    function getResponse() {
        var response = this.response;
        var deferred = $q.defer();
        if (this.wait) {
            $timeout(function() {
                deferred.resolve(response);
            });
        } else {
            deferred.resolve(response);
        }

        return deferred.promise;
    }
});
