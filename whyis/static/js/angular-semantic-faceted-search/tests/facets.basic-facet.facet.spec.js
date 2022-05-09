/* eslint-env jasmine */
/* global inject, module, _  */

describe('BasicFacet', function() {
    var $rootScope, $q, $timeout, mock, mockConstructor, BasicFacet, facet,
        options, natResponse, genResponse;

    beforeEach(module('seco.facetedSearch'));

    beforeEach(module(function($provide) {
        mock = {
            getObjectsNoGrouping: getResponse
        };
        mockConstructor = function() { return mock; };

        $provide.value('AdvancedSparqlService', mockConstructor);
    }));

    beforeEach(inject(function() {
        spyOn(mock, 'getObjectsNoGrouping').and.callThrough();
    }));

    beforeEach(inject(function(_$timeout_, _$q_, _$rootScope_, _BasicFacet_) {
        $timeout = _$timeout_;
        $q = _$q_;
        $rootScope = _$rootScope_;
        BasicFacet = _BasicFacet_;

        options = {
            endpointUrl: 'endpoint',
            name: 'Name',
            facetId: 'textId',
            predicate: '<pred>',
            enabled: true
        };

        facet = new BasicFacet(options);

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
        facet = new BasicFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should take its initial value from the config if present', function() {
        var iv = 'initial text';
        options.initial = { 'textId': { value: iv } };
        facet = new BasicFacet(options);

        expect(facet.getSelectedValue()).toEqual(iv);
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new BasicFacet(options);

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
            var value = '<http://ldf.fi/narc-menehtyneet1939-45/sukupuoli/Mies>';
            facet.state = _.cloneDeep(genResponse);
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.setSelectedValue(value);

            expect(facet.getSelectedValue()).toEqual(value);
            expect(facet.selectedValue).toEqual(genResponse[1]);

            facet.setSelectedValue(undefined);

            expect(facet.getSelectedValue()).toBeUndefined();
            expect(facet.selectedValue).toEqual(genResponse[0]);
        });
    });

    describe('deselectValue', function() {
        it('should select the "no selection" value', function() {
            var value = '<http://ldf.fi/narc-menehtyneet1939-45/sukupuoli/Mies>';

            facet.state = _.cloneDeep(genResponse);
            expect(facet.getSelectedValue()).toBeUndefined();

            facet.setSelectedValue(value);
            expect(facet.getSelectedValue()).toEqual(value);

            facet.deselectValue();
            expect(facet.selectedValue).toEqual(genResponse[0]);
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

            expect(facet.getConstraint()).toEqual(' ?id <pred> <obj> . ');
        });
    });

    describe('getPriority', function() {
        it('should return the priority value', function() {
            expect(facet.getPriority()).toBeUndefined();

            facet.config.priority = 20;

            expect(facet.getPriority()).toEqual(20);

            options.priority = 30;
            facet = new BasicFacet(options);

            expect(facet.getPriority()).toEqual(30);
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
            '   SELECT DISTINCT ?cnt ?value ?facet_text { ' +
            '    {' +
            '     SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) ?value {' +
            '      ?id <p> <o> . ' +
            '      ?id <pred> ?value . ' +
            '     } GROUP BY ?value ' +
            '    } ' +
            '    FILTER(BOUND(?value)) ' +
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
            '    BIND(COALESCE(?lbl, IF(!ISURI(?value), ?value, "")) AS ?facet_text)' +
            '   }' +
            '  }' +
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

        it('should make a query to each service given in the config', function() {
            options.services = ['<service>'];
            facet = new BasicFacet(options);

            var cons = [' ?id a <http://ldf.fi/schema/narc-menehtyneet1939-45/DeathRecord> . ?id skos:prefLabel ?name .'];
            var data = { facets: {}, constraint: cons };
            mock.response = natResponse;

            facet.update(data);
            $rootScope.$apply();

            expect(mock.getObjectsNoGrouping).toHaveBeenCalledTimes(2);
            mock.getObjectsNoGrouping.calls.reset();

            options.services = ['<service>', '<service2>'];
            facet = new BasicFacet(options);

            facet.update(data);
            $rootScope.$apply();

            expect(mock.getObjectsNoGrouping).toHaveBeenCalledTimes(3);
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
