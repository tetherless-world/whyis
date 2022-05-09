/* eslint-env jasmine */
/* global inject, module  */

describe('TimespanFacet', function() {
    var TimespanFacet, timespanMapperService, facet, options;

    beforeEach(module('seco.facetedSearch'));
    beforeEach(inject(function(_TimespanFacet_, _timespanMapperService_) {

        TimespanFacet = _TimespanFacet_;
        timespanMapperService = _timespanMapperService_;

        options = {
            name: 'Timespan',
            startPredicate: '<http://ldf.fi/start>',
            endPredicate: '<http://ldf.fi/end>',
            facetId: 'spanId',
            min: '1939-10-01',
            max: '1989-12-31',
            enabled: true
        };

        facet = new TimespanFacet(options);

    }));

    it('should be enabled if config says so', function() {
        expect(facet.isEnabled()).toBe(true);
    });

    it('should be disabled if config says so', function() {
        options.enabled = false;
        facet = new TimespanFacet(options);

        expect(facet.isEnabled()).toBe(false);
    });

    it('should get its initial value from config', function() {
        var d = '1945-02-02';
        var val = { start: d, end: d };
        options.initial = { spanId: { value: val } };

        var facet = new TimespanFacet(options);

        expect(facet.getSelectedValue()).toEqual(val);

        val = { start: d };
        options.initial = { spanId: { value: val } };

        facet = new TimespanFacet(options);

        expect(facet.getSelectedValue()).toEqual(val);

        val = { end: d };
        options.initial = { spanId: { value: val } };

        facet = new TimespanFacet(options);

        expect(facet.getSelectedValue()).toEqual(val);
    });

    describe('enable', function() {
        it('should enable the facet', function() {
            options.enabled = false;
            facet = new TimespanFacet(options);

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
        it('should get the selected values as strings', function() {
            var ds = new Date(1945,0,1);
            var de = new Date(1946,1,2);
            var val = { start: ds, end: de };
            facet.selectedValue = val;

            var expected = {
                start: '1945-01-01',
                end: '1946-02-02'
            };

            expect(facet.getSelectedValue()).toEqual(expected);
        });
    });

    describe('getConstraint', function() {
        it('should return a constraint based on the selected value', function() {
            var start = new Date('1945-02-02');
            var end = new Date('1945-03-02');

            var val = { start: start, end: end };
            facet.selectedValue = val;

            var filter = 'FILTER(<http://www.w3.org/2001/XMLSchema#date>(?start_spanId) >= "' + start.toISOString().slice(0, 10) +
                    '"^^<http://www.w3.org/2001/XMLSchema#date>)';

            var isIncluded = (facet.getConstraint().indexOf(filter) > -1);
            expect(isIncluded).toBe(true);

            filter = 'FILTER(<http://www.w3.org/2001/XMLSchema#date>(?end_spanId) <= "' + end.toISOString().slice(0, 10) +
                    '"^^<http://www.w3.org/2001/XMLSchema#date>)';

            isIncluded = (facet.getConstraint().indexOf(filter) > -1);
            expect(isIncluded).toBe(true);
        });

        it('should use only one variable if start and end properties are the same', function() {
            options.endPredicate = options.startPredicate;
            facet = new TimespanFacet(options);

            var start = new Date('1945-02-02');
            var end = new Date('1945-03-02');

            var val = { start: start, end: end };
            facet.selectedValue = val;

            var filter = 'FILTER(<http://www.w3.org/2001/XMLSchema#date>(?start_spanId) >= "' + start.toISOString().slice(0, 10) +
                    '"^^<http://www.w3.org/2001/XMLSchema#date>)';

            var isIncluded = (facet.getConstraint().indexOf(filter) > -1);
            expect(isIncluded).toBe(true);

            filter = 'FILTER(<http://www.w3.org/2001/XMLSchema#date>(?start_spanId) <= "' + end.toISOString().slice(0, 10) +
                    '"^^<http://www.w3.org/2001/XMLSchema#date>)';

            isIncluded = (facet.getConstraint().indexOf(filter) > -1);
            expect(isIncluded).toBe(true);
        });
    });

    describe('updateState', function() {
        it('should update the facet state based on the given dates', function() {
            var val = {
                min: timespanMapperService.parseValue('1940-10-10'),
                max: timespanMapperService.parseValue('1941-10-11')
            };

            var expected = {
                start: {
                    minDate: timespanMapperService.parseValue('1940-10-10'),
                    maxDate: timespanMapperService.parseValue('1941-10-11'),
                    initDate: timespanMapperService.parseValue('1940-10-10'),
                    startingDay: 1
                },
                end: {
                    minDate: timespanMapperService.parseValue('1940-10-10'),
                    maxDate: timespanMapperService.parseValue('1941-10-11'),
                    initDate: timespanMapperService.parseValue('1941-10-11'),
                    startingDay: 1
                }
            };
            expect(facet.updateState(val)).toEqual(expected);
        });

        it('should respect the configured minimum and maximum dates', function() {
            var val = {
                min: timespanMapperService.parseValue('1910-10-10'),
                max: timespanMapperService.parseValue('2000-10-11')
            };

            var expected = {
                start: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1939-10-01'),
                    startingDay: 1
                },
                end: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1989-12-31'),
                    startingDay: 1
                }
            };
            expect(facet.updateState(val)).toEqual(expected);
        });

        it('should update only the maximum selectable date if the minumum is too early', function() {
            var val = {
                min: timespanMapperService.parseValue('1910-10-10'),
                max: timespanMapperService.parseValue('1950-10-11')
            };

            var expected = {
                start: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1950-10-11'),
                    initDate: timespanMapperService.parseValue('1939-10-01'),
                    startingDay: 1
                },
                end: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1950-10-11'),
                    initDate: timespanMapperService.parseValue('1950-10-11'),
                    startingDay: 1
                }
            };
            expect(facet.updateState(val)).toEqual(expected);
        });

        it('should update only the minumum selectable date if the maximum is too late', function() {
            var val = {
                min: timespanMapperService.parseValue('1950-10-11'),
                max: timespanMapperService.parseValue('2000-10-11')
            };

            var expected = {
                start: {
                    minDate: timespanMapperService.parseValue('1950-10-11'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1950-10-11'),
                    startingDay: 1
                },
                end: {
                    minDate: timespanMapperService.parseValue('1950-10-11'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1989-12-31'),
                    startingDay: 1
                }
            };
            expect(facet.updateState(val)).toEqual(expected);
        });

        it('should not break if it is called with undefined dates', function() {
            var val = { min: undefined, max: undefined };

            var expected = {
                start: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1939-10-01'),
                    startingDay: 1
                },
                end: {
                    minDate: timespanMapperService.parseValue('1939-10-01'),
                    maxDate: timespanMapperService.parseValue('1989-12-31'),
                    initDate: timespanMapperService.parseValue('1989-12-31'),
                    startingDay: 1
                }
            };
            expect(facet.updateState(val)).toEqual(expected);
        });
    });
});
