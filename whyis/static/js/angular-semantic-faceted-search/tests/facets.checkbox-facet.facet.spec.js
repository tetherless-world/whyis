/* eslint-env jasmine */
/* global inject, module, _ */

describe('CheckboxFacet', function() {
    var $rootScope, $q, $timeout, mock, mockConstructor, CheckboxFacet, facet,
        options, natResponse, genResponse;

    beforeEach(module('seco.facetedSearch'));

    beforeEach(module(function($provide) {
        mock = {
            getObjectsNoGrouping: getResponse
        };
        mockConstructor = function() { return mock; };

        $provide.value('AdvancedSparqlService', mockConstructor);
    }));

    beforeEach(inject(function(){
        spyOn(mock, 'getObjectsNoGrouping').and.callThrough();
    }));

    beforeEach(inject(function(_$timeout_, _$q_, _$rootScope_, _CheckboxFacet_) {
        $timeout = _$timeout_;
        $q = _$q_;
        $rootScope = _$rootScope_;
        CheckboxFacet = _CheckboxFacet_;

        options = {
            endpointUrl: 'endpoint',
            name: 'Name',
            facetId: 'textId',
            choices: [
                {
                    id: 'wikipedia',
                    pattern: '?id <http://ldf.fi/norssit/wikipedia> [] .',
                    label: 'Wikipedia'
                },
                {
                    id: 'kansallisbiografia',
                    pattern: '?id <http://ldf.fi/norssit/kansallisbiografia> [] .',
                    label: 'Kansallisbiografia'
                }
            ],
            enabled: true
        };

        facet = new CheckboxFacet(options);

        genResponse = [
            {
                'value': 'wikipedia',
                'text': 'Wikipedia',
                'count': 94286
            },
            {
                'value': 'kansallisbiografia',
                'text': 'Kansallisbiografia',
                'count': 405
            }
        ];

        natResponse = [
            {
                'value': 'wikipedia',
                'text': 'Wikipedia',
                'count': 666
            },
            {
                'value': 'kansallisbiografia',
                'text': 'Kansallisbiografia',
                'count': 666
            }
        ];


    }));

    it('should be enabled if config says so', function() {
        expect(facet.isEnabled()).toBe(true);
    });

    it('should be disabled if config says so', function() {
        options.enabled = false;
        facet = new CheckboxFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should take its initial value from the config if present', function() {
        var iv = 'initial text';
        options.initial = { 'textId': { value: iv } };
        facet = new CheckboxFacet(options);

        expect(facet.getSelectedValue()).toEqual(iv);
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new CheckboxFacet(options);

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

    describe('setSelectedValue', function() {
        it('should set the selected value', function() {
            var value = 'wikipedia';
            facet.state = genResponse;
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.setSelectedValue(value);

            expect(facet.getSelectedValue()).toEqual([value]);
            expect(facet.selectedValue).toEqual({ value: ['wikipedia'] });
        });

        it('should should add another selected value, if a value is already selected', function() {
            facet.state = genResponse;
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.setSelectedValue('wikipedia');
            facet.setSelectedValue('kansallisbiografia');

            expect(facet.getSelectedValue()).toEqual(['wikipedia', 'kansallisbiografia']);
            expect(facet.selectedValue).toEqual({ value: ['wikipedia', 'kansallisbiografia'] });
        });
    });

    describe('deselectValue', function() {
        it('should deselect the given selected value', function() {
            var first = 'wikipedia';
            var second = 'kansallisbiografia';

            facet.state = _.cloneDeep(genResponse);
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.setSelectedValue(first);
            expect(facet.getSelectedValue()).toEqual([first]);

            facet.deselectValue(first);
            expect(facet.selectedValue).toEqual({ value: [] });

            facet.setSelectedValue(first);
            facet.setSelectedValue(second);
            expect(facet.getSelectedValue()).toEqual([first, second]);

            facet.deselectValue(first);
            expect(facet.selectedValue).toEqual({ value: [second] });

            facet.setSelectedValue(first);
            facet.deselectValue(second);
            expect(facet.selectedValue).toEqual({ value: [first] });
        });
    });

    describe('getSelectedValue', function() {
        it('should get the selected value', function() {
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.selectedValue = { value: ['<obj>'] };

            expect(facet.getSelectedValue()).toEqual(['<obj>']);
        });
    });

    describe('getConstraint', function() {
        it('should return a constraint based on the selected value', function() {
            facet.selectedValue = { value: ['"wikipedia"'] };

            expect(facet.getConstraint()).toEqual('?id <http://ldf.fi/norssit/wikipedia> [] .');
        });
    });

    describe('buildQuery', function() {
        it('should build a valid query', function() {
            var cons = ['?id <p> <o> .'];

            var expected =
            ' PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' +
            ' PREFIX skos: <http://www.w3.org/2004/02/skos/core#> ' +
            ' PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ' +
            ' SELECT DISTINCT ?value ?facet_text ?cnt WHERE { ' +
            '   { ' +
            '     SELECT DISTINCT (COUNT(DISTINCT(?id)) AS ?cnt) ("wikipedia" AS ?value) ("Wikipedia" AS ?facet_text) { ' +
            '       ?id <p> <o> . ' +
            '       BIND("wikipedia" AS ?val) ?id <http://ldf.fi/norssit/wikipedia> [] . ' +
            '     } ' +
            '     GROUP BY ?val' +
            '   } UNION { ' +
            '     SELECT DISTINCT (COUNT(DISTINCT(?id)) AS ?cnt) ("kansallisbiografia" AS ?value) ("Kansallisbiografia" AS ?facet_text) { ' +
            '       ?id <p> <o> . ' +
            '       BIND("kansallisbiografia" AS ?val) ?id <http://ldf.fi/norssit/kansallisbiografia> [] . ' +
            '     } ' +
            '     GROUP BY ?val' +
            '   } ' +
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
