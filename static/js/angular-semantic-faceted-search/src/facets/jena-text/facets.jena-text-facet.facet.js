(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .value('textQueryPredicate', '<http://jena.apache.org/text#query>')
    .factory('JenaTextFacet', JenaTextFacet);

    /* ngInject */
    function JenaTextFacet(_, TextFacet, textQueryPredicate) {

        JenaTextFacet.prototype = Object.create(TextFacet.prototype);
        JenaTextFacet.prototype.getConstraint = getConstraint;
        JenaTextFacet.prototype.sanitize = sanitize;

        return JenaTextFacet;

        function JenaTextFacet(options) {
            TextFacet.call(this, options);
            this.config.priority = this.config.priority || 0;
        }

        function getConstraint() {
            var value = this.getSelectedValue();
            if (!value) {
                return undefined;
            }

            value = this.sanitize(value);

            var args = [];
            if (this.config.predicate) {
                args.push(this.config.predicate);
            }

            args.push('"' + value + '"');

            if (this.config.limit) {
                args.push(this.config.limit);
            }

            var obj = '(' + args.join(' ') + ')';

            var result = '(?id ?score) ' + textQueryPredicate + ' ' + obj + ' .';

            if (this.config.graph) {
                result = 'GRAPH ' + this.config.graph + ' { ' + result + ' }';
            }

            return result || undefined;
        }

        function sanitize(query) {
            query = query
                .replace(/[\\()]/g, '') // backslashes, and parentheses
                .replace(/~{2,}/g, '~') // double ~
                .replace(/^~/g, '') // ~ as first token
                .replace(/(\b~*(AND|OR|NOT)\s*~*)+$/g, '') // AND, OR, NOT last
                .replace(/^((AND|OR|NOT)\b\s*~*)+/g, ''); // AND, OR, NOT first

            var quoteRepl;
            if ((query.match(/"/g) || []).length % 2) {
                // Unbalanced quotes, remove them
                quoteRepl = '';
            } else {
                // Balanced quotes, escape them
                quoteRepl = '\\"';
            }
            query = query.replace(/"/g, quoteRepl).trim();

            return query;
        }
    }
})();
