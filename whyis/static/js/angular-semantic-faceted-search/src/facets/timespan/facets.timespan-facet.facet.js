
/*
* Facet for selecting a date range
*/
(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .factory('TimespanFacet', TimespanFacet);

    /* ngInject */
    function TimespanFacet($q, _, facetEndpoint, timespanMapperService, BasicFacet,
            PREFIXES) {
        TimespanFacetConstructor.prototype = Object.create(BasicFacet.prototype);

        TimespanFacetConstructor.prototype.getSelectedValue = getSelectedValue;
        TimespanFacetConstructor.prototype.getConstraint = getConstraint;
        TimespanFacetConstructor.prototype.buildQueryTemplate = buildQueryTemplate;
        TimespanFacetConstructor.prototype.buildQuery = buildQuery;
        TimespanFacetConstructor.prototype.fetchState = fetchState;
        TimespanFacetConstructor.prototype.update = update;
        TimespanFacetConstructor.prototype.disable = disable;
        TimespanFacetConstructor.prototype.enable = enable;
        TimespanFacetConstructor.prototype.getOtherSelections = getOtherSelections;
        TimespanFacetConstructor.prototype.initState = initState;
        TimespanFacetConstructor.prototype.getMinDate = getMinDate;
        TimespanFacetConstructor.prototype.getMaxDate = getMaxDate;
        TimespanFacetConstructor.prototype.getSelectedStartDate = getSelectedStartDate;
        TimespanFacetConstructor.prototype.getSelectedEndDate = getSelectedEndDate;
        TimespanFacetConstructor.prototype.updateState = updateState;

        return TimespanFacetConstructor;

        function TimespanFacetConstructor(options) {
            var simpleTemplate = PREFIXES +
            ' SELECT (min(xsd:date(?value)) AS ?min) (max(xsd:date(?value)) AS ?max) { ' +
            '   <SELECTIONS> ' +
            '   ?id <START_PROPERTY> ?value . ' +
            ' } ';

            var separateTemplate = PREFIXES +
            ' SELECT ?min ?max { ' +
            '   { ' +
            '     SELECT (min(xsd:date(?start)) AS ?min) { ' +
            '       <SELECTIONS> ' +
            '       ?id <START_PROPERTY> ?start . ' +
            '     } ' +
            '   } ' +
            '   { ' +
            '     SELECT (max(xsd:date(?end)) AS ?max) { ' +
            '       <SELECTIONS> ' +
            '       ?id <END_PROPERTY> ?end . ' +
            '     } ' +
            '   } ' +
            ' } ';

            var defaultConfig = {};

            this.config = angular.extend({}, defaultConfig, options);

            this.name = this.config.name;
            this.facetId = this.config.facetId;
            this.startPredicate = this.config.startPredicate;
            this.endPredicate = this.config.endPredicate;

            if (angular.isString(this.config.min)) {
                this.minDate = timespanMapperService.parseValue(this.config.min);
            } else {
                this.minDate = this.config.min;
            }
            if (angular.isString(this.config.max)) {
                this.maxDate = timespanMapperService.parseValue(this.config.max);
            } else {
                this.maxDate = this.config.max;
            }

            this.initState();

            if (this.config.enabled) {
                this.enable();
            } else {
                this.disable();
            }

            this.config.mapper = timespanMapperService;

            this.endpoint = facetEndpoint.getEndpoint(this.config);

            this.queryTemplate = this.buildQueryTemplate(
                this.startPredicate === this.endPredicate ? simpleTemplate : separateTemplate);

            this.varSuffix = this.facetId;

            this.selectedValue = {};

            // Initial value
            var initial = _.get(options, 'initial.' + this.facetId);
            if (initial && initial.value) {
                this._isEnabled = true;
                this.selectedValue = {};
                if (initial.value.start) {
                    this.selectedValue.start = timespanMapperService.parseValue(initial.value.start);
                }
                if (initial.value.end) {
                    this.selectedValue.end = timespanMapperService.parseValue(initial.value.end);
                }
            }
        }

        function initState() {
            if (!this.state) {
                this.state = {};
            }

            this.state.start = {
                minDate: this.getMinDate(),
                maxDate: this.getMaxDate(),
                initDate: this.getMinDate(),
                startingDay: this.config.startingDay || 1
            };

            this.state.end = {
                minDate: this.getMinDate(),
                maxDate: this.getMaxDate(),
                initDate: this.getMaxDate(),
                startingDay: this.config.startingDay || 1
            };
        }

        function update(constraints) {
            var self = this;
            if (!self.isEnabled()) {
                return $q.when();
            }

            var otherCons = this.getOtherSelections(constraints.constraint);
            if (self.otherCons === otherCons) {
                // Only this facet's selection has changed
                self.updateState({ min: self.getMinDate(), max: self.getMaxDate() });
                return $q.when(self.state);
            }
            self.otherCons = otherCons;

            self._isBusy = true;

            return self.fetchState(constraints).then(function(state) {
                if (!_.isEqual(self.otherCons, otherCons)) {
                    return $q.reject('Facet state changed');
                }
                self.state = state;
                self._isBusy = false;

                return state;
            });
        }


        function getMinDate() {
            return _.clone(this.minDate);
        }

        function getMaxDate() {
            return _.clone(this.maxDate);
        }

        function enable() {
            BasicFacet.prototype.enable.call(this);
        }

        function disable() {
            BasicFacet.prototype.disable.call(this);
            this.initState();
        }

        function buildQueryTemplate(template) {
            return template
                .replace(/<START_PROPERTY>/g, this.startPredicate)
                .replace(/<END_PROPERTY>/g, this.endPredicate)
                .replace(/\s+/g, ' ');
        }

        function buildQuery(constraints) {
            constraints = constraints || [];
            var query = this.queryTemplate
                .replace(/<SELECTIONS>/g, this.getOtherSelections(constraints));
            return query;
        }

        function getOtherSelections(constraints) {
            var ownConstraint = this.getConstraint();

            var selections = _.reject(constraints, function(v) { return v === ownConstraint; });
            return selections.join(' ');
        }

        // Build a query with the facet selection and use it to get the facet state.
        function fetchState(constraints) {
            var self = this;

            var query = self.buildQuery(constraints.constraint);

            return self.endpoint.getObjectsNoGrouping(query).then(function(results) {
                var state = _.first(results);

                self.updateState(state);

                self._error = false;

                return self.state;
            }).catch(function(error) {
                self._isBusy = false;
                self._error = true;
                return $q.reject(error);
            });
        }

        function updateState(minMax) {
            var self = this;

            var minDate = self.getMinDate();
            if (!minMax.min || minMax.min < minDate) {
                minMax.min = minDate;
            }

            var maxDate = self.getMaxDate();
            if (!minMax.max || minMax.max > maxDate) {
                minMax.max = maxDate;
            }

            var selectedStart = self.getSelectedStartDate();
            self.state.start.initDate = selectedStart || minMax.min;
            self.state.start.minDate = minMax.min;
            self.state.start.maxDate = minMax.max;

            var selectedEnd = self.getSelectedEndDate();
            self.state.end.initDate = selectedEnd || minMax.max;
            self.state.end.minDate = minMax.min;
            self.state.end.maxDate = minMax.max;

            if (selectedEnd < self.state.start.maxDate) {
                self.state.start.maxDate = selectedEnd;
            }

            if (selectedStart > self.state.end.minDate) {
                self.state.end.minDate = selectedStart;
            }

            return self.state;
        }

        function getSelectedStartDate() {
            return _.clone((this.selectedValue || {}).start);
        }

        function getSelectedEndDate() {
            return _.clone((this.selectedValue || {}).end);
        }

        function getSelectedValue() {
            if (!this.selectedValue) {
                return;
            }
            var selectedValue = {};
            if (this.selectedValue.start) {
                selectedValue.start = getISOStringFromDate(this.selectedValue.start);
            }
            if (this.selectedValue.end) {
                selectedValue.end = getISOStringFromDate(this.selectedValue.end);
            }
            return selectedValue;
        }

        function getConstraint() {
            var result =
            ' <START_FILTER> ' +
            ' <END_FILTER> ';

            var value = this.getSelectedValue() || {};

            var start = value.start;
            var end = value.end;

            if (!(start || end)) {
                return '';
            }

            var startFilter =
            ' ?id <START_PROPERTY> <VAR> . ' +
            ' FILTER(<http://www.w3.org/2001/XMLSchema#date>(<VAR>) >= "<START_VALUE>"^^<http://www.w3.org/2001/XMLSchema#date>) ';

            var endFilter =
            ' ?id <END_PROPERTY> <VAR> . ' +
            ' FILTER(<http://www.w3.org/2001/XMLSchema#date>(<VAR>) <= "<END_VALUE>"^^<http://www.w3.org/2001/XMLSchema#date>) ';

            var startVar = '?start_' + this.varSuffix;
            var endVar = '?end_' + this.varSuffix;

            if (this.startPredicate === this.endPredicate) {
                endVar = startVar;
            }

            startFilter = startFilter.replace(/<VAR>/g, startVar);
            endFilter = endFilter.replace(/<VAR>/g, endVar);

            if (start) {
                result = result
                    .replace('<START_FILTER>',
                        startFilter.replace('<START_PROPERTY>',
                            this.startPredicate))
                    .replace('<START_VALUE>', start);
            } else {
                result = result.replace('<START_FILTER>', '');
            }
            if (end) {
                result = result
                    .replace('<END_FILTER>',
                        endFilter.replace('<END_PROPERTY>',
                            this.endPredicate))
                    .replace('<END_VALUE>', end);
            } else {
                result = result.replace('<END_FILTER>', '');
            }
            return result;
        }

        function getISOStringFromDate(d) {
            var mm = (d.getMonth() + 1).toString();
            var dd = d.getDate().toString();
            mm = mm.length === 2 ? mm : '0' + mm;
            dd = dd.length === 2 ? dd : '0' + dd;

            return [d.getFullYear(), mm, dd].join('-');
        }
    }
})();
