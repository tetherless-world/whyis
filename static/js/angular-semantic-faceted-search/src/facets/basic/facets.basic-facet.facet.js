
/*
* Facet for selecting a simple value.
*/
(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .factory('BasicFacet', BasicFacet);

    /* ngInject */
    function BasicFacet($q, _, facetEndpoint, NO_SELECTION_STRING, PREFIXES) {

        BasicFacetConstructor.prototype.update = update;
        BasicFacetConstructor.prototype.getState = getState;
        BasicFacetConstructor.prototype.fetchState = fetchState;
        BasicFacetConstructor.prototype.fetchFacetTextFromServices = fetchFacetTextFromServices;
        BasicFacetConstructor.prototype.finalizeFacetValues = finalizeFacetValues;
        BasicFacetConstructor.prototype.getConstraint = getConstraint;
        BasicFacetConstructor.prototype.getTriplePattern = getTriplePattern;
        BasicFacetConstructor.prototype.getSpecifier = getSpecifier;
        BasicFacetConstructor.prototype.getPriority = getPriority;
        BasicFacetConstructor.prototype.buildQueryTemplate = buildQueryTemplate;
        BasicFacetConstructor.prototype.buildQuery = buildQuery;
        BasicFacetConstructor.prototype.buildSelections = buildSelections;
        BasicFacetConstructor.prototype.buildLabelPart = buildLabelPart;
        BasicFacetConstructor.prototype.removeOwnConstraint = removeOwnConstraint;
        BasicFacetConstructor.prototype.getOtherSelections = getOtherSelections;
        BasicFacetConstructor.prototype.getDeselectUnionTemplate = getDeselectUnionTemplate;
        BasicFacetConstructor.prototype.disable = disable;
        BasicFacetConstructor.prototype.enable = enable;
        BasicFacetConstructor.prototype.isLoading = isLoading;
        BasicFacetConstructor.prototype.isEnabled = isEnabled;
        BasicFacetConstructor.prototype.hasError = hasError;
        BasicFacetConstructor.prototype.getSelectedValue = getSelectedValue;
        BasicFacetConstructor.prototype.setSelectedValue = setSelectedValue;
        BasicFacetConstructor.prototype.deselectValue = deselectValue;

        return BasicFacetConstructor;

        function BasicFacetConstructor(options) {

            /* Implementation */

            this.previousConstraints;
            this.state = {};

            var labelPart =
            ' OPTIONAL {' +
            '  ?labelValue skos:prefLabel ?lbl . ' +
            '  FILTER(langMatches(lang(?lbl), "<PREF_LANG>")) .' +
            ' }' +
            ' OPTIONAL {' +
            '  ?labelValue rdfs:label ?lbl . ' +
            '  FILTER(langMatches(lang(?lbl), "<PREF_LANG>")) .' +
            ' }';

            var serviceQueryTemplate = PREFIXES +
            ' SELECT DISTINCT ?facet_text ?value {' +
            '  VALUES ?value { <VALUES> } ' +
            '  ?value skos:prefLabel|rdfs:label [] . ' +
            '  BIND(?value AS ?labelValue) ' +
            '  <LABEL_PART>' +
            '  BIND(?lbl AS ?facet_text)' +
            '  FILTER(?facet_text != "")' +
            ' }';

            var queryTemplate = PREFIXES +
            ' SELECT DISTINCT ?cnt ?facet_text ?value WHERE {' +
            ' { ' +
            '  { ' +
            '   SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) { ' +
            '    <OTHER_SELECTIONS> ' +
            '   } ' +
            '  } ' +
            '  BIND("<NO_SELECTION_STRING>" AS ?facet_text) ' +
            ' } UNION ' +
            '  {' +
            '   SELECT DISTINCT ?cnt ?value ?facet_text { ' +
            '    {' +
            '     SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) ?value {' +
            '      <SELECTIONS> ' +
            '     } GROUP BY ?value ' +
            '    } ' +
            '    FILTER(BOUND(?value))' +
            '    BIND(COALESCE(?value, <http://ldf.fi/NONEXISTENT_URI>) AS ?labelValue) ' +
            '    <LABEL_PART> ' +
            '    BIND(COALESCE(?lbl, IF(!ISURI(?value), ?value, "")) AS ?facet_text)' +
            '   } ' +
            '  }' +
            ' } ';

            var defaultConfig = {
                preferredLang: 'fi',
                queryTemplate: queryTemplate,
                serviceQueryTemplate: serviceQueryTemplate,
                labelPart: labelPart,
                noSelectionString: NO_SELECTION_STRING,
                usePost: true
            };

            this.config = angular.extend({}, defaultConfig, options);

            this.name = this.config.name;
            this.facetId = this.config.facetId;
            this.predicate = this.config.predicate;
            this.specifier = this.config.specifier;
            if (this.config.enabled) {
                this.enable();
            } else {
                this.disable();
            }

            this.endpoint = facetEndpoint.getEndpoint(this.config);

            // Initial value
            var constVal = _.get(options, 'initial.' + this.facetId);

            if (constVal && constVal.value) {
                this._isEnabled = true;
                this.selectedValue = { value: constVal.value };
            }

            this.labelPart = this.buildLabelPart();
            this.queryTemplate = this.buildQueryTemplate(this.config.queryTemplate);
            this.serviceQueryTemplate = this.buildQueryTemplate(this.config.serviceQueryTemplate);
        }

        function update(constraints) {
            var self = this;
            if (!self.isEnabled()) {
                return $q.when();
            }

            var otherCons = this.getOtherSelections(constraints.constraint);
            if (self.otherCons === otherCons) {
                return $q.when(self.state);
            }
            self.otherCons = otherCons;

            self._isBusy = true;

            return self.fetchState(constraints).then(function(state) {
                if (!_.isEqual(otherCons, self.otherCons)) {
                    return $q.reject('Facet state changed');
                }
                self.state = state;
                self._isBusy = false;

                return state;
            });
        }

        function getState() {
            return this.state;
        }

        // Build a query with the facet selection and use it to get the facet state.
        function fetchState(constraints) {
            var self = this;

            var query = self.buildQuery(constraints.constraint);

            return self.endpoint.getObjectsNoGrouping(query).then(function(results) {
                if (self.config.services) {
                    return self.fetchFacetTextFromServices(results);
                }
                self._error = false;
                return results;
            }).then(function(res) {
                res = self.finalizeFacetValues(res);
                self._error = false;
                return res;
            }).catch(function(error) {
                self._isBusy = false;
                self._error = true;
                return $q.reject(error);
            });
        }

        function finalizeFacetValues(results) {
            results.forEach(function(r) {
                if (!r.text) {
                    r.text = r.value.replace(/^.+\/(.+?)>$/, '$1');
                }
            });
            return [_.head(results)].concat(_.sortBy(_.tail(results), 'text'));
        }

        function fetchFacetTextFromServices(results) {
            var self = this;
            var emptyLabels = _.filter(results, function(r) { return !r.text; });
            var values = _.map(emptyLabels, function(r) { return r.value; });
            var promises = _.map(self.config.services, function(s) {
                var endpointConfig = {
                    endpointUrl: s.replace(/[<>]/g, ''),
                    usePost: self.config.usePost,
                    headers: self.config.headers
                };
                var endpoint = facetEndpoint.getEndpoint(endpointConfig);
                var qry = self.serviceQueryTemplate
                    .replace(/<VALUES>/g, values.join(' '));
                return endpoint.getObjectsNoGrouping(qry);
            });
            return $q.all(promises).then(function(res) {
                var all = _.flatten(res);
                all.forEach(function(objWithText) {
                    _.find(results, ['value', objWithText.value]).text = objWithText.text;
                });
                return results;
            });
        }

        function hasError() {
            return this._error;
        }

        function getTriplePattern() {
            return '?id ' + this.predicate + ' ?value . ';
        }

        function getSpecifier() {
            return this.specifier ? this.specifier : '';
        }

        function getPriority() {
            return this.config.priority;
        }

        function getConstraint() {
            if (!this.getSelectedValue()) {
                return;
            }
            if (this.getSelectedValue()) {
                return ' ?id ' + this.predicate + ' ' + this.getSelectedValue() + ' . ';
            }
        }

        function getDeselectUnionTemplate() {
            return this.deselectUnionTemplate;
        }

        // Build the facet query
        function buildQuery(constraints) {
            constraints = constraints || [];
            var otherConstraints = this.removeOwnConstraint(constraints);
            var query = this.queryTemplate
                .replace(/<OTHER_SELECTIONS>/g, otherConstraints.join(' '))
                .replace(/<SELECTIONS>/g, this.buildSelections(otherConstraints));

            return query;
        }

        function buildSelections(constraints) {
            constraints = constraints.join(' ') +
                ' ' + this.getTriplePattern() +
                ' ' + this.getSpecifier();
            return constraints;
        }

        function removeOwnConstraint(constraints) {
            var ownConstraint = this.getConstraint();
            return _.reject(constraints, function(v) { return v === ownConstraint; });
        }

        function getOtherSelections(constraints) {
            return this.removeOwnConstraint(constraints).join(' ');
        }

        function buildLabelPart() {
            var self = this;
            var res = '';
            var langs = _.castArray(self.config.preferredLang).concat(['']);
            langs.forEach(function(lang) {
                res += self.config.labelPart.replace(/<PREF_LANG>/g, lang);
            });
            return res;
        }

        // Replace placeholders in the query template using the configuration.
        function buildQueryTemplate(template) {
            var templateSubs = [
                {
                    placeHolder: /<LABEL_PART>/g,
                    value: this.labelPart
                },
                {
                    placeHolder: /<NO_SELECTION_STRING>/g,
                    value: this.config.noSelectionString
                },
                {
                    placeHolder: /\s+/g,
                    value: ' '
                }
            ];

            templateSubs.forEach(function(s) {
                template = template.replace(s.placeHolder, s.value);
            });
            return template;
        }

        function getSelectedValue() {
            var val;
            if (this.selectedValue) {
                val = this.selectedValue.value;
            }
            return val;
        }

        function setSelectedValue(value) {
            this.selectedValue = _.find(this.getState(), ['value', value]);
        }

        function deselectValue() {
            this.setSelectedValue(undefined);
        }

        function isEnabled() {
            return this._isEnabled;
        }

        function enable() {
            this._isEnabled = true;
        }

        function disable() {
            this.selectedValue = undefined;
            this._isEnabled = false;
        }

        function isLoading() {
            return this._isBusy;
        }
    }
})();
