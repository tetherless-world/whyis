(function() {

    'use strict';

    /**
    * @ngdoc object
    * @name sparql.AdvancedSparqlService
    * @requires sparql.SparqlService
    * @requires sparql.PagerService
    * @requires sparql.objectMapperService
    */
    angular.module('sparql')
    .factory('AdvancedSparqlService', AdvancedSparqlService);

    /* ngInject */
    function AdvancedSparqlService($http, $q, SparqlService, PagerService, objectMapperService) {

        /**
        * @ngdoc function
        * @name sparql.AdvancedSparqlService
        * @constructor
        * @description
        * Service for querying a SPARQL endpoint, with paging support.
        * @param {Object|string} configuration Configuration object or the SPARQL endpoit URL as a string.
        *   The object has the following properties:
        *
        *   - **endpointUrl** - `{string}` - The SPARQL endpoint URL.
        *   - **usePost** - `{boolean}` - If truthy, use POST instead of GET. Default is `false`.
        * @param {Object} [mapper=objectMapperService] Object that maps the SPARQL results as objects.
        * The mapper should provide 'makeObjectList' and 'makeObjectListNoGrouping'
        * functions that take the SPARQL results as parameter and return the mapped objects.
        * @example
        * <pre>
        * var config = { endpointUrl: 'http://dbpedia.org/sparql', usePost: false };
        * var endpoint = new AdvancedSparqlServiceSparqlService(config, objectMapperService);
        * // Or using just a string parameter:
        * endpoint = new AdvancedSparqlService('http://dbpedia.org/sparql');
        *
        * var resultSet = '?id a <http://dbpedia.org/ontology/Writer> .';
        *
        * var queryTemplate =
        * 'SELECT * WHERE { ' +
        * ' <RESULT_SET ' +
        * ' OPTIONAL { ?id rdfs:label ?label . } ' +
        * '}';
        *
        * var queryBuilder = new QueryBuilderService(prefixes);
        * var qryObj = queryBuilder.buildQuery(qry, resultSet, '?id');
        *
        * var resultPromise = endpoint.getObjects(qryObj.query, 10, qryObj.resultSetQry, 1);
        * </pre>
        */
        return function(configuration, mapper) {
            var endpoint = new SparqlService(configuration);

            mapper = mapper || objectMapperService;

            var self = this;

            self.getObjects = getObjects;
            self.getObjectsNoGrouping = getObjectsNoGrouping;

            /**
            * @ngdoc method
            * @methodOf sparql.AdvancedSparqlService
            * @name sparql.AdvancedSparqlService#getObjects
            * @description
            * Get the SPARQL query results as a list of objects as mapped by the mapper
            * given at init. Results are paged using `PagerService` if `pageSize` is given.
            * This uses the `makeObjectList` method of the mapper.
            * @param {string} sparqlQry The SPARQL query.
            * @param {number} [pageSize] The page size.
            * @param {string} [resultSetQry] The query that defines the result set
            *   of the query (`sparqlQry`). I.e. a sub query that returns the
            *   distinct URIs of all the resources to be paged. Required if pageSize
            *   is given, i.e. when results should be paged.
            * @param {number} [pagesPerQuery] The number of pages to get per query.
            * @returns {promise} A promise of the list of the query results as objects,
            *   or if pageSize was gicen, a promise of a `PagerService` instance.
            * @example
            * <pre>
            * var prefixes =
            * 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' +
            * 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ';
            *
            * // Note the `<PAGE>` placeholder
            * var resultSet =
            * ' { ' +
            * '   SELECT DISTINCT ?id { ' +
            * '     ?id a <http://dbpedia.org/ontology/Writer> . ' +
            * '   } ORDER BY ?id <PAGE> ' +
            * ' } ';
            *
            * var qry = prefixes +
            * 'SELECT * WHERE { ' +
            *   resultSet +
            * ' OPTIONAL { ?id rdfs:label ?label . } ' +
            * '}';
            *
            * var resultSetQry = prefixes + resultSet;
            * var resultPromise = endpoint.getObjects(qry, 10, resultSetQry, 1);
            *
            * // Or you can use the `QueryBuilderService` for convenience:
            *
            * var resultSet = '?id a <http://dbpedia.org/ontology/Writer> .';
            *
            * var queryTemplate =
            * 'SELECT * WHERE { ' +
            * ' <RESULT_SET ' +
            * ' OPTIONAL { ?id rdfs:label ?label . } ' +
            * '}';
            *
            * var queryBuilder = new QueryBuilderService(prefixes);
            * var qryObj = queryBuilder.buildQuery(qry, resultSet, '?id');
            *
            * var resultPromise = endpoint.getObjects(qryObj.query, 10, qryObj.resultSetQry, 1);
            * </pre>
            */
            function getObjects(sparqlQry, pageSize, resultSetQry, pagesPerQuery) {
                // Get the results as objects.
                // If pageSize is defined, return a (promise of a) PagerService object, otherwise
                // query the endpoint and return the results as a promise.
                if (pageSize) {
                    return $q.when(new PagerService(sparqlQry, resultSetQry, pageSize,
                            getResultsWithGrouping, pagesPerQuery));
                }
                // Query the endpoint.
                return getResultsWithGrouping(sparqlQry.replace('<PAGE>', ''));
            }

            /**
            * @ngdoc method
            * @methodOf sparql.AdvancedSparqlService
            * @name sparql.AdvancedSparqlService#getObjectsNoGrouping
            * @description
            * Get the SPARQL query results as a list of objects. Results are paged
            * if `pageSize` is given. This uses the `makeObjectListNoGrouping` method
            * of the mapper.
            * @param {string} sparqlQry The SPARQL query.
            * @param {number} [pageSize] The page size.
            * @param {number} [pagesPerQuery] The number of pages to get per query.
            * @returns {promise} A promise of the list of the query results as objects,
            *   or if pageSize was given, a promise of a `PagerService` instance.
            * @example
            * <pre>
            * var qry =
            * 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ';
            * 'SELECT * WHERE { ' +
            * ' ?id a <http://dbpedia.org/ontology/Writer> . ' +
            * ' OPTIONAL { ?id rdfs:label ?label . } ' +
            * '}';
            *
            * var resultPromise = endpoint.getObjects(qry, 10, 1);
            *
            * // Without paging:
            * var resultPromise = endpoint.getObjects(qry);
            * </pre>
            */
            function getObjectsNoGrouping(sparqlQry, pageSize, pagesPerQuery) {
                // Get the results as objects but call 'makeObjectListNoGrouping' instead
                // (i.e. treat each result as a separate object and don't group by id).
                // If pageSize is defined, return a (promise of a) PagerService object, otherwise
                // query the endpoint and return the results as a promise.
                if (pageSize) {
                    return $q.when(new PagerService(sparqlQry, pageSize,
                        getResultsNoGrouping, pagesPerQuery));
                }
                // Query the endpoint.
                return getResultsNoGrouping(sparqlQry.replace('<PAGE>', ''));
            }

            function getResultsWithGrouping(sparqlQry, raw) {
                var promise = endpoint.getObjects(sparqlQry);
                if (raw) {
                    return promise;
                }
                return promise.then(function(data) {
                    return mapper.makeObjectList(data);
                });
            }

            function getResultsNoGrouping(sparqlQry, raw) {
                var promise = endpoint.getObjects(sparqlQry);
                if (raw) {
                    return promise;
                }
                return promise.then(function(data) {
                    return mapper.makeObjectListNoGrouping(data);
                });
            }
        };
    }
})();
