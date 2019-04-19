/* eslint-env jasmine */
/* global inject, module  */

describe('JenaTextFacet', function() {
    var JenaTextFacet, facet, options, subPred;

    beforeEach(module('seco.facetedSearch'));
    beforeEach(inject(function(_JenaTextFacet_) {

        JenaTextFacet = _JenaTextFacet_;

        options = {
            name: 'Name',
            facetId: 'textId',
            enabled: true
        };

        facet = new JenaTextFacet(options);

        subPred = '(?id ?score) <http://jena.apache.org/text#query> ';

    }));

    it('should be enabled if config says so', function() {
        expect(facet.isEnabled()).toBe(true);
    });

    it('should be disabled if config says so', function() {
        options.enabled = false;
        facet = new JenaTextFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should get its initial value from config', function() {
        options.initial = { textId: { value: 'value' } };

        var facet = new JenaTextFacet(options);

        expect(facet.getSelectedValue()).toEqual('value');
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new JenaTextFacet(options);

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

        it('should should not change the case of the search', function() {
            var searchTerms = 'FoO BBAR';
            facet.selectedValue = searchTerms;

            var cons = facet.getConstraint();

            var isIncluded = (cons.indexOf(searchTerms) > -1);
            expect(isIncluded).toBe(true);
        });

        it('should remove quotes if they are unbalanced', function() {
            facet.selectedValue = '"blaa blaa';

            var expected = subPred + '("blaa blaa") .';
            expect(facet.getConstraint()).toEqual(expected);

            facet.selectedValue = '"blaa foo" bar"';

            expected = subPred + '("blaa foo bar") .';
            expect(facet.getConstraint()).toEqual(expected);
        });

        it('should excape quotes if they are balanced', function() {
            facet.selectedValue = '"blaa blaa"';

            var expected = subPred + '("\\\"blaa blaa\\\"") .';
            expect(facet.getConstraint()).toEqual(expected);

            facet.selectedValue = 'blaa "blaa" "foo" bar';

            expected = subPred + '("blaa \\\"blaa\\\" \\\"foo\\\" bar") .';
            expect(facet.getConstraint()).toEqual(expected);
        });

        it('should return a valid constraint if no property is given', function() {
            var searchTerms = 'foo bar';

            facet.selectedValue = searchTerms;
            var cons = facet.getConstraint();

            var expected = subPred + '("foo bar") .';

            expect(cons).toEqual(expected);
        });

        it('should return a valid constraint if a property is given', function() {
            var searchTerms = 'foo bar';
            var pred = '<pred>';

            options.predicate = pred;
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            var cons = facet.getConstraint();

            var expected = subPred + '(<pred> "foo bar") .';

            expect(cons).toEqual(expected);
        });

        it('should use the limit if given', function() {
            var searchTerms = 'foo bar';
            var pred = '<pred>';

            options.limit = 10;
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            var cons = facet.getConstraint();

            var expected = subPred + '("foo bar" 10) .';

            expect(cons).toEqual(expected);

            options.predicate = pred;
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            cons = facet.getConstraint();

            expected = subPred + '(<pred> "foo bar" 10) .';

            expect(cons).toEqual(expected);
        });

        it('should use the graph if given', function() {
            var searchTerms = 'foo bar';
            var pred = '<pred>';

            options.graph = '<graph>';
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            var cons = facet.getConstraint().replace(/\s+/g, ' ');

            var expected = 'GRAPH <graph> { ' + subPred + '("foo bar") . }';

            expect(cons).toEqual(expected);

            options.predicate = pred;
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            cons = facet.getConstraint().replace(/\s+/g, ' ');

            expected = 'GRAPH <graph> { ' + subPred + '(<pred> "foo bar") . }';

            expect(cons).toEqual(expected);

            options.limit = 100;
            facet = new JenaTextFacet(options);

            facet.selectedValue = searchTerms;
            cons = facet.getConstraint().replace(/\s+/g, ' ');

            expected = 'GRAPH <graph> { ' + subPred + '(<pred> "foo bar" 100) . }';

            expect(cons).toEqual(expected);
        });

        it('should remove ~ from the beginning of the query', function() {
            var searchTerms = {
                '~foo bar': 'foo bar',
                '~~foo bar': 'foo bar',
                '~foo~ bar': 'foo~ bar'
            };

            Object.keys(searchTerms).forEach(function(query) {
                facet.selectedValue = query;
                var cons = facet.getConstraint();

                var expected = subPred + '("' + searchTerms[query] + '") .';

                expect(cons).toEqual(expected);
            });
        });

        it('should remove double ~ from the query', function() {
            var searchTerms = {
                'foo~~ bar~': 'foo~ bar~',
                'foo~~~ bar~': 'foo~ bar~',
                'foo~~~ bar~~~': 'foo~ bar~'
            };

            Object.keys(searchTerms).forEach(function(query) {
                facet.selectedValue = query;
                var cons = facet.getConstraint();

                var expected = subPred + '("' + searchTerms[query] + '") .';

                expect(cons).toEqual(expected);
            });
        });

        it('should remove AND, OR, and NOT if they are the first or last part of a query', function() {
            var searchTerms = {
                'foo bar AND': 'foo bar',
                'foo bar AND NOT': 'foo bar',
                'foo bar AND NOT OR': 'foo bar',
                'foo bar OR': 'foo bar',
                'foo bar NOT': 'foo bar',
                'AND': '',
                '~AND': '',
                '~~AND': '',
                'AND~': '',
                'AND~~': '',
                '~AND~~': '',
                'NOT~': '',
                'NOT': '',
                'OR': '',
                'AND foo bar AND': 'foo bar',
                'AND foo bar': 'foo bar',
                'OR foo bar AND NOT': 'foo bar',
                'NOT foo bar AND NOT OR': 'foo bar',
                'AND OR NOT foo bar OR': 'foo bar',
                'OR NOT foo bar NOT': 'foo bar'
            };

            Object.keys(searchTerms).forEach(function(query) {
                facet.selectedValue = query;
                var cons = facet.getConstraint();

                var expected = subPred + '("' + searchTerms[query] + '") .';

                expect(cons).toEqual(expected);
            });
        });

        it('should not remove AND, OR, and NOT if they are part of the first or last word', function() {
            var searchTerms = {
                'foo barAND': 'foo barAND',
                'foo barAND NOT': 'foo barAND',
                'foo barAND NOT OR': 'foo barAND',
                'foo barOR': 'foo barOR',
                'foo barNOT': 'foo barNOT',
                'barNOT': 'barNOT',
                'barAND': 'barAND',
                'ANDbarOR': 'ANDbarOR',
                'ORbar': 'ORbar',
                'NOTbar': 'NOTbar'
            };

            Object.keys(searchTerms).forEach(function(query) {
                facet.selectedValue = query;
                var cons = facet.getConstraint();

                var expected = subPred + '("' + searchTerms[query] + '") .';

                expect(cons).toEqual(expected);
            });
        });
        it('should remove parentheses, and backslashes', function() {
            var searchTerms = [
                'foo bar (',
                'foo bar )',
                'foo bar ()',
                'foo bar \\',
                'foo bar (\\\\)'
            ];

            searchTerms.forEach(function(query) {
                facet.selectedValue = query;
                var cons = facet.getConstraint();

                var expected = subPred + '("foo bar") .';

                expect(cons).toEqual(expected);
            });
        });
    });
});
