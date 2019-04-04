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
            '     SELECT DISTINCT (count(DISTINCT ?id) as ?cnt) ?value ?hierarchy ?lvl {' +
            '      { SELECT DISTINCT ?h { [] <ID> ?h . <SPECIFIER> } } ' +
            '      ?h (<HIERARCHY>)* ?value . ' +
            '      <LEVELS> ' +
            '      ?id <ID> ?h .' +
            '      <OTHER_SELECTIONS> ' +
            '     } GROUP BY ?hierarchy ?value ?lvl ORDER BY ?hierarchy ' +
            '    } ' +
            '    FILTER(BOUND(?value))' +
            '    BIND(COALESCE(?value, <http://ldf.fi/NONEXISTENT_URI>) AS ?labelValue) ' +
            '    <LABEL_PART> ' +
            '    BIND(COALESCE(?lbl, STR(?value)) as ?label) ' +
            '    BIND(CONCAT(?lvl, ?label) as ?facet_text)' +
            '   } ' +
            '  } ' +
            ' } ';

            options.queryTemplate = options.queryTemplate || queryTemplate;
            options.depth = angular.isUndefined(options.depth) ? 3 : options.depth;

            BasicFacet.call(this, options);

            this.selectedValue;

            // Initial value
            var constVal = _.get(options, 'initial.' + this.facetId);
            if (constVal && constVal.value) {
                this._isEnabled = true;
                this.selectedValue = { value: constVal.value };
            }

            var triplePatternTemplate =
                ' ?<V_VAR> (<HIERARCHY>)* <SELECTED_VAL> . <SPECIFIER> ?id <ID> ?<V_VAR> . ';

            this.triplePatternTemplate = this.buildQueryTemplate(triplePatternTemplate);
        }

        function buildQueryTemplate(template) {
            var templateSubs = [
                {
                    placeHolder: /<ID>/g,
                    value: this.predicate
                },
                {
                    placeHolder: /<HIERARCHY>/g,
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
                    placeHolder: /<V_VAR>/g,
                    value: 'seco_v_' + this.facetId
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

        function getConstraint() {
            if (!this.getSelectedValue()) {
                return;
            }
            var res = this.triplePatternTemplate
                .replace(/<SELECTED_VAL>/g, this.getSelectedValue())
                .replace(/<SPECIFIER>/g, this.getSpecifier().replace(/\?value/g, '?seco_v_' + this.facetId));

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
                .replace(/<LEVELS>/g, buildLevels(this.config.depth, this.config.hierarchy))
                .replace(/<SPECIFIER>/g, this.getSpecifier().replace(/\?value\b/g, '?h'));

            return query;
        }

        function buildLevels(count, hierarchyProperty) {
            var res = '';
            var template = ' OPTIONAL { ?value <PROPERTY> ?u0 . <HIERARCHY> }';
            for (var i = count; i > 0; i--) {
                var hierarchy = _.map(_.range(i - 1), function(n) { return '?u' + n + ' <PROPERTY> ?u' + (n + 1) + ' . '; }).join('') +
                    'BIND(CONCAT(' + _.map(_.rangeRight(i), function(n) { return 'STR(?u' + n + '),'; }).join('') + 'STR(?value)) AS ?_h) ' +
                    'BIND("' + _.repeat('-', i) + ' " AS ?lvl)';
                res = res += template.replace('<HIERARCHY>', hierarchy);
            }
            var end = ' OPTIONAL { BIND("" AS ?lvl) } BIND(COALESCE(?_h, STR(?value)) AS ?hierarchy) ';
            return res.replace(/<PROPERTY>/g, hierarchyProperty) + end;
        }
    }
})();
