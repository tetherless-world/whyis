(function() {
    'use strict';

    /**
    * @ngdoc object
    * @name seco.facetedSearch.FacetResultHandler
    */
    angular.module('seco.facetedSearch')
    .constant('DEFAULT_PAGES_PER_QUERY', 1)
    .constant('DEFAULT_RESULTS_PER_PAGE', 10)

    /*
    * Result handler service.
    */
    .factory('FacetResultHandler', FacetResultHandler);

    /* @ngInject */
    function FacetResultHandler(_, DEFAULT_PAGES_PER_QUERY, DEFAULT_RESULTS_PER_PAGE,
            PREFIXES, AdvancedSparqlService, objectMapperService, QueryBuilderService) {

        return ResultHandler;

        /**
        * @name seco.facetedSearch.FacetResultHandler
        * @ngdoc function
        * @constructor
        * @description
        * Service for retrieving SPARQL results based on facet selections.
        *
        * @param {string} endpointConfig The URL of the SPARQL endpoint,
        *  or a configuration object as taken by {@link http://semanticcomputing.github.io/angular-paging-sparql-service/#/api/sparql.AdvancedSparqlService `AdvancedSparqlService`}.
        *  See the {@link https://github.com/SemanticComputing/angular-paging-sparql-service angular-paging-sparql-service} package.
        * @param {Object} resultOptions Configuration object.
        *   The object has the following properties:
        *
        *   - **queryTemplate** - `{string}` - The result query with a `<RESULT_SET>`
        *     placeholder for the facet selections.
        *     The variable `?id` should be used for the result resources.
        *     The query should not restrict the results in any way (outside of the
        *     facet selections), or the results will not reflect the facets.
        *     The best way to insure this is to wrap each result value in an
        *     `OPTIONAL` block.
        *     For example:
        *      <pre>
        *      SELECT * WHERE {
        *          <RESULT_SET>
        *          OPTIONAL {
        *              ?id rdfs:label ?name .
        *              FILTER(langMatches(lang(?name), "en"))
        *          }
        *      }
        *      </pre>
        *   - **[prefixes]** - `{string}` - Any prefixes used in the `queryTemplate`.
        *     Required if the query uses any other prefixes than `rdf`, `rdfs`, or `skos`.
        *   - **[paging]** - `{boolean}` - If truthy, results will be paged.
        *     Default is `true`.
        *   - **[resultsPerPage]** - `{number}` - The number of results per page.
        *     Default is 10.
        *   - **[pagesPerQuery]** - `{number}` - The number of pages to retrieve per query.
        *     Default is 1.
        *   - **[mapper]** - `{Object}` - Mapper service for the results.
        *     The default is
        *     {@link http://semanticcomputing.github.io/angular-paging-sparql-service/#/api/sparql.objectMapperService `objectMapperService`}.
        *     See the {@link https://github.com/SemanticComputing/angular-paging-sparql-service angular-paging-sparql-service} package
        *     for more information.
        *
        */
        function ResultHandler(endpointConfig, resultOptions) {
            // Default options
            var options = {
                resultsPerPage: DEFAULT_RESULTS_PER_PAGE,
                pagesPerQuery: DEFAULT_PAGES_PER_QUERY,
                mapper: objectMapperService,
                prefixes: PREFIXES,
                paging: true
            };
            options = angular.extend(options, resultOptions);

            /* Public API */

            this.getResults = getResults;

            /* Implementation */

            var qryBuilder = new QueryBuilderService(options.prefixes);

            var endpoint = new AdvancedSparqlService(endpointConfig, options.mapper);

            /**
            * @ngdoc method
            * @methodOf seco.facetedSearch.FacetResultHandler
            * @name seco.facetedSearch.FacetResultHandler#getResults
            * @description
            * Get results based on the facet selections and the query template.
            * Use paging if defined in the options.
            * @param {Object} facetSelections The facet states as broadcast by
            *   {@link seco.facetedSearch.FacetHandler `FacetHandler`}
            * @param {string} [orderBy] SPARQL order comparators to use in sorting
            *   the results. Any variables used here have to be present in the
            *   `<RESULT_SET>` part of the query. I.e. they need to be included
            *   in the `constraint` parameter of
            *   {@link seco.facetedSearch.FacetHandler `FacetHandler`}.
            *   The default is to sort by `?id`.
            */
            function getResults(facetSelections, orderBy) {
                var constraints = facetSelections.constraint.join(' ');
                var qry = qryBuilder.buildQuery(options.queryTemplate, constraints, orderBy);

                if (options.paging) {
                    return endpoint.getObjects(qry.query, options.resultsPerPage, qry.resultSetQuery,
                        options.pagesPerQuery);
                } else {
                    return endpoint.getObjects(qry.query);
                }
            }
        }
    }
})();
