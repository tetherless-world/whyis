
/*
* Facet for selecting a date range
*/
(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .factory('CheckboxFacet', CheckboxFacet);

    /* ngInject */
    function CheckboxFacet($q, _, facetEndpoint, BasicFacet, PREFIXES) {
        CheckboxFacet.prototype = Object.create(BasicFacet.prototype);

        CheckboxFacet.prototype.getConstraint = getConstraint;
        CheckboxFacet.prototype.buildQueryTemplate = buildQueryTemplate;
        CheckboxFacet.prototype.buildQuery = buildQuery;
        CheckboxFacet.prototype.fetchState = fetchState;
        CheckboxFacet.prototype.deselectValue = deselectValue;
        CheckboxFacet.prototype.setSelectedValue = setSelectedValue;

        return CheckboxFacet;

        function CheckboxFacet(options) {

            var queryTemplate = PREFIXES +
            ' SELECT DISTINCT ?value ?facet_text ?cnt WHERE { ' +
            '  <PREDICATE_UNION> ' +
            ' } ';

            var predTemplate =
            ' { ' +
            '  SELECT DISTINCT (COUNT(DISTINCT(?id)) AS ?cnt) ("<ID>" AS ?value)' +
            '     ("<LABEL>" AS ?facet_text) { ' +
            '   <SELECTIONS> ' +
            '   BIND("<ID>" AS ?val) ' +
            '   <PREDICATE> ' +
            '  } GROUP BY ?val ' +
            ' } ';

            var defaultConfig = {
                usePost: true
            };

            this.config = angular.extend({}, defaultConfig, options);

            this.name = this.config.name;
            this.facetId = this.config.facetId;
            this.state = {};

            if (this.config.enabled) {
                this.enable();
            } else {
                this.disable();
            }

            this.endpoint = facetEndpoint.getEndpoint(this.config);

            this.queryTemplate = this.buildQueryTemplate(queryTemplate, predTemplate);

            this.selectedValue = {};

            // Initial value
            var initial = _.get(options, 'initial[' + this.facetId + '].value');
            if (initial) {
                this._isEnabled = true;
                this.selectedValue = { value: initial };
            }
        }

        function buildQueryTemplate(template, predTemplate) {
            var unions = '';
            this.config.choices.forEach(function(pred) {
                var union = predTemplate
                    .replace(/<ID>/g, pred.id)
                    .replace(/<PREDICATE>/g, pred.pattern)
                    .replace(/<LABEL>/g, pred.label);
                if (unions) {
                    union = ' UNION ' + union;
                }
                unions += union;
            });

            return template
                .replace(/<PREDICATE_UNION>/g, unions)
                .replace(/\s+/g, ' ');
        }

        function buildQuery(constraints) {
            constraints = constraints || [];
            var query = this.queryTemplate
                .replace(/<SELECTIONS>/g, this.getOtherSelections(constraints));
            return query;
        }

        // Build a query with the facet selection and use it to get the facet state.
        function fetchState(constraints) {
            var self = this;

            var query = self.buildQuery(constraints.constraint);

            return self.endpoint.getObjectsNoGrouping(query).then(function(results) {
                self._error = false;
                return results;
            }).catch(function(error) {
                self._isBusy = false;
                self._error = true;
                return $q.reject(error);
            });
        }

        function setSelectedValue(value) {
            this.selectedValue.value = _.uniq((this.selectedValue.value || []).concat(value));
        }

        function deselectValue(value) {
            _.pull(this.selectedValue.value, value);
        }

        function getConstraint() {
            var self = this;
            var selections = _.compact(self.getSelectedValue());
            if (!(selections.length)) {
                return;
            }
            var res = '';
            selections.forEach(function(val) {
                var cons = _.get(_.find(self.config.choices, ['id', val.replace(/"/g, '')]), 'pattern');
                if (res) {
                    cons = ' UNION { ' + cons + ' } ';
                } else if (selections.length > 1) {
                    cons = ' { ' + cons + ' } ';
                }
                res += cons;
            });

            return res;
        }
    }
})();
