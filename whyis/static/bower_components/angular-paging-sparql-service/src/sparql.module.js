(function() {
    'use strict';

    /**
     * @ngdoc overview
     * @name index
     * @description
     * # Angular SPARQL service with paging and object mapping
     * Angular services for querying SPARQL endpoints, and mapping the results
     * as simple objects.
     * Provided injectable services:
     *
     * {@link sparql.SparqlService SparqlService} provides a constructor for a simple SPARQL query service
     * that simply returns results (bindings) based on a SPARQL query.
     *
     * {@link sparql.AdvancedSparqlService AdvancedSparqlService} provides the same service as SparqlService, but adds
     * paging support for queries.
     *
     * {@link sparql.QueryBuilderService QueryBuilderService} can be used to construct pageable SPARQL queries.
     *
     * {@link sparql.objectMapperService objectMapperService} maps SPARQL results to objects.
     */

    /**
     * @ngdoc overview
     * @name sparql
     * @description
     * # Angular SPARQL service with paging and object mapping
     * Main module.
     */
    angular.module('sparql', [])
    .constant('_', _); // eslint-disable-line no-undef
})();
