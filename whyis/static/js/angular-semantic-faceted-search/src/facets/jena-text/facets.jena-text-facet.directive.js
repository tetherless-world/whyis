(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoJenaTextFacet
    * @restrict 'E'
    * @element ANY
    * @description
    * A free-text search facet using Jena text search.
    *
    * This facet can only be used if the SPARQL endpoint supports
    * [Jena text query](https://jena.apache.org/documentation/query/text-query.html).
    *
    * The facet does not make any SPARQL queries, just generates SPARQL triple patterns
    * out of the typed text for other facets to use.
    *
    * The produced constraint looks like the following (where `predicate`, and `limit`
    * are based on the configuration options, and left out if undefined):
    * <pre>
    * (?id ?score) <http://jena.apache.org/text#query> (predicate "search terms" limit) .
    * </pre>
    *
    * If the `graph` option is defined, the constraint is wrapped accordingly:
    * <pre>
    * GRAPH graph {
    *   (?id ?score) <http://jena.apache.org/text#query> (predicate "search terms" limit) .
    * }
    * </pre>
    *
    * The score is captured as variable `?score`, and can thus be used to sort results.
    *
    * The search terms are sanitized in order to avoid syntax errors from the backend.
    * In case there is an even number of quotes (`"`) they are escaped in the search terms.
    * If there is an odd number of quotes, they are removed.
    * Backslashes, and parentheses are removed, as well as `AND`, `OR`, and `NOT`,
    * if they are the first or last tokens in the query.
    * "`~`" is removed if it's the first character in the query.
    * Consecutive "`~`" are removed. I.e. "`~~`" is changed to "`~`".
    * Otherwise the search terms are not modified, so e.g. `AND`, `OR`, `*`, and `~`
    * can be used in the query.
    *
    * The sanitization is not reflected to the user, so if a search triggers while
    * they are writing, and the last word they wrote is, e.g., "`AND`",
    * the user will see all that they wrote, but the produced SPARQL constraint
    * will not include the `AND`. The user can continue writing, and the next time
    * the search triggers, if the query is valid, the constraint will include it.
    *
    * @param {Object} options The configuration object with the following structure:
    * - **facetId** - `{string}` - A friendly id for the facet.
    *   Should be unique in the set of facets, and should be usable as a SPARQL variable.
    * - **name** - `{string}` - The title of the facet. Will be displayed to end users.
    * - **[enabled]** `{boolean}` - Whether or not the facet is enabled by default.
    *   If undefined, the facet will be disabled by default.
    * - **[priority]** - `{number}` - Priority for constraint sorting. Default is 0.
    * - **[predicate]** - `{string}` - The property to use in the search.
    *   See [Jena text query documentation](https://jena.apache.org/documentation/query/text-query.html#query-with-sparql).
    * - **[limit]** - `{number}` - Limit for the text search results.
    *   See [Jena text query documentation](https://jena.apache.org/documentation/query/text-query.html#query-with-sparql).
    * - **[graph]** - `{string}` - The URI of the graph to use for the text search.
    *
    */
    angular.module('seco.facetedSearch')
    .directive('secoJenaTextFacet', jenaTextFacet);

    function jenaTextFacet() {
        return {
            restrict: 'E',
            scope: {
                options: '='
            },
            controller: 'JenaTextFacetController',
            controllerAs: 'vm',
            templateUrl: 'src/facets/text/facets.text-facet.directive.html'
        };
    }
})();
