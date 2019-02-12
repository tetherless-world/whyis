/* eslint-env jasmine */
/* global inject, module  */

describe('TextFacet', function() {
    var TextFacet, facet, options;

    beforeEach(module('seco.facetedSearch'));
    beforeEach(inject(function(_TextFacet_) {

        TextFacet = _TextFacet_;

        options = {
            name: 'Name',
            facetId: 'textId',
            predicate: '<http://www.w3.org/2004/02/skos/core#prefLabel>',
            enabled: true
        };

        facet = new TextFacet(options);

    }));

    it('should be enabled if config says so', function() {
        expect(facet.isEnabled()).toBe(true);
    });

    it('should be disabled if config says so', function() {
        options.enabled = false;
        facet = new TextFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should get its initial value from config', function() {
        options.initial = { textId: { value: 'value' } };

        var facet = new TextFacet(options);

        expect(facet.getSelectedValue()).toEqual('value');
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new TextFacet(options);

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

    describe('clear', function() {
        it('should clear the selected value', function() {
            facet.selectedValue = 'blaa';

            facet.clear();

            expect(facet.getSelectedValue()).toBeUndefined();
        });
    });

    describe('getSelectedValue', function() {
        it('should get the selected value', function() {
            facet.selectedValue = 'blaa';

            expect(facet.getSelectedValue()).toEqual('blaa');
        });
    });

    describe('getConstraint', function() {
        it('should return a constraint based on the selected value', function() {
            facet.selectedValue = 'blaa';

            var isIncluded = (facet.getConstraint().indexOf('blaa') > -1);

            expect(isIncluded).toBe(true);
        });

        it('should should lowercase the value', function() {
            var searchTerms = ['FoO', 'BBAR'];
            facet.selectedValue = searchTerms.join(' ');

            var cons = facet.getConstraint();
            searchTerms.forEach(function(term) {
                var isIncluded = (cons.indexOf(term.toLowerCase()) > -1);
                expect(isIncluded).toBe(true);
            });
        });

        it('should should split the search terms if there are multiple words', function() {
            var searchTerms = ['foooz', 'barzz'];
            facet.selectedValue = searchTerms.join(' ');

            var cons = facet.getConstraint();

            var isIncluded = (cons.indexOf(searchTerms.join(' ')) > -1);
            expect(isIncluded).toBe(false);

            searchTerms.forEach(function(term) {
                isIncluded = (cons.indexOf(term.toLowerCase()) > -1);
                expect(isIncluded).toBe(true);
            });
        });
    });
});
