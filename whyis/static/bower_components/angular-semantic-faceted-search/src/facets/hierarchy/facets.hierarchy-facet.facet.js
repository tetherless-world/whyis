/*
* Facet for selecting a simple value.
*/
(function() {
    'use strict';

    angular.module('seco.facetedSearch')

    .factory('HierarchyFacet', HierarchyFacet);

    /* ngInject */
    function HierarchyFacet($q, _, BasicFacet, PREFIXES) {

        HierarchyFacetConstructor.prototype = Object.create(BasicFacet.prototype);

        HierarchyFacetConstructor.prototype.getSelectedValue = getSelectedValue;
        HierarchyFacetConstructor.prototype.getConstraint = getConstraint;
        HierarchyFacetConstructor.prototype.buildQueryTemplate = buildQueryTemplate;
        HierarchyFacetConstructor.prototype.buildQuery = buildQuery;
        HierarchyFacetConstructor.prototype.getHierarchyClasses = getHierarchyClasses;
        HierarchyFacetConstructor.prototype.fetchState = fetchState;

        return HierarchyFacetConstructor;

        function HierarchyFacetConstructor(options) {

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
            '   SELECT DISTINCT ?cnt ?value ?facet_text {' +
            '    {' +
            '     SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) ?value ?class {' +
            '      VALUES ?class { ' +
            '       <HIERARCHY_CLASSES> ' +
            '      } ' +
            '      ?value <PROPERTY> ?class . ' +
            '      ?h <PROPERTY> ?value . ' +
            '      ?id <ID> ?h .' +
            '      <OTHER_SELECTIONS> ' +
            '     } GROUP BY ?class ?value ' +
            '    } ' +
            '    FILTER(BOUND(?value))' +
            '    <LABEL_PART> ' +
            '    BIND(COALESCE(?lbl, STR(?value)) as ?label)' +
            '    BIND(IF(?value = ?class, ?label, CONCAT("-- ", ?label)) as ?facet_text)' +
            '    BIND(IF(?value = ?class, 0, 1) as ?order)' +
            '   } ORDER BY ?class ?order ?facet_text' +
            '  } ' +
            ' } ';

            options.queryTemplate = options.queryTemplate || queryTemplate;

            BasicFacet.call(this, options);

            this.selectedValue;

            // Initial value
            var constVal = _.get(options, 'initial.' + this.facetId);
            if (constVal && constVal.value) {
                this._isEnabled = true;
                this.selectedValue = { value: constVal.value };
            }

            var triplePatternTemplate =
            ' VALUES ?<CLASS_VAR> { ' +
            '  <HIERARCHY_CLASSES> ' +
            ' } ' +
            ' ?<H_VAR> <PROPERTY> ?<CLASS_VAR> . ' +
            ' ?<V_VAR> <PROPERTY> ?<H_VAR> . ' +
            ' ?id <ID> ?<V_VAR> .';

            this.triplePatternTemplate = this.buildQueryTemplate(triplePatternTemplate);
        }

        function buildQueryTemplate(template) {
            var templateSubs = [
                {
                    placeHolder: /<ID>/g,
                    value: this.predicate
                },
                {
                    placeHolder: /<PROPERTY>/g,
                    value: this.config.hierarchy
                },
                {
                    placeHolder: /<LABEL_PART>/g,
                    value: this.labelPart
                },
                {
                    placeHolder: /<NO_SELECTION_STRING>/g,
                    value: this.config.noSelectionString
                },
                {
                    placeHolder: /<H_VAR>/g,
                    value: 'seco_h_' + this.facetId
                },
                {
                    placeHolder: /<V_VAR>/g,
                    value: 'seco_v_' + this.facetId
                },
                {
                    placeHolder: /<CLASS_VAR>/g,
                    value: 'seco_class_' + this.facetId
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

        function getHierarchyClasses() {
            return this.config.classes || [];
        }

        function getConstraint() {
            if (!this.getSelectedValue()) {
                return;
            }
            var res = this.triplePatternTemplate
                .replace(/<HIERARCHY_CLASSES>/g, this.getSelectedValue());

            return res;
        }

        function getSelectedValue() {
            var val;
            if (this.selectedValue) {
                val = this.selectedValue.value;
            }
            return val;
        }

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

        // Build the facet query
        function buildQuery(constraints) {
            constraints = constraints || [];
            var query = this.queryTemplate
                .replace(/<OTHER_SELECTIONS>/g, this.getOtherSelections(constraints))
                .replace(/<HIERARCHY_CLASSES>/g,
                    this.getSelectedValue() || this.getHierarchyClasses().join(' '));

            return query;
        }
    }
})();
