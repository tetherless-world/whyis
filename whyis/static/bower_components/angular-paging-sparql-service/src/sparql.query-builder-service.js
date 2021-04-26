(function() {

    'use strict';

    /**
    * @ngdoc object
    * @name sparql.QueryBuilderService
    */
    angular.module('sparql')
    .factory('QueryBuilderService', QueryBuilderService);

    /**
    * @ngdoc function
    * @name sparql.QueryBuilderService
    * @constructor
    * @description
    * Service for building pageable SPARQL queries.
    * @param {string} Prefixes prefixes used in the SPARQL query.
    * @example
    * <pre>
    * var prefixes =
    * 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' +
    * 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ';
    *
    * var queryBuilder = new QueryBuilderService(prefixes);
    *
    * var resultSet = '?id a <http://dbpedia.org/ontology/Writer> .';
    *
    * var queryTemplate =
    * 'SELECT * WHERE { ' +
    * ' <RESULT_SET ' +
    * ' OPTIONAL { ?id rdfs:label ?label . } ' +
    * '}';
    *
    * var qryObj = queryBuilder.buildQuery(qry, resultSet, '?id');
    *
    * // qryObj.query returns (without line breaks):
    * // PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    * // PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    * // SELECT * WHERE {
    * //   {
    * //     SELECT DISTINCT ?id {
    * //       ?id a <http://dbpedia.org/ontology/Writer>.
    * //     } ORDER BY ?id <PAGE>
    * //   }
    * //   OPTIONAL { ?id rdfs:label ?label . }
    * // }
    *
    * // qryObj.resultSetQry returns (without line breaks):
    * // PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    * // PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    * // SELECT DISTINCT ?id {
    * //   ?id a <http://dbpedia.org/ontology/Writer>.
    * // } ORDER BY ?id <PAGE>
    * </pre>
    */
    /* ngInject */
    function QueryBuilderService() {

        var resultSetQryShell =
        '  SELECT DISTINCT ?id { ' +
        '   <CONTENT> ' +
        '  } ORDER BY <ORDER_BY> <PAGE> ';

        var resultSetShell =
        ' { ' +
        '   <RESULT_SET> ' +
        ' } FILTER(BOUND(?id)) ';

        return QueryBuilder;

        function QueryBuilder(prefixes) {

            return {
                buildQuery : buildQuery
            };

            /**
            * @ngdoc method
            * @methodOf sparql.QueryBuilderService
            * @name sparql.QueryBuilderService#buildQuery
            * @description
            * Build a pageable SPARQL query.
            * @param {string} queryTemplate The SPARQL query with `<RESULT_SET>`
            *   as a placeholder for the result set query, which is a subquery
            *   that returns the distinct URIs of all the resources to be paged.
            *   The resource URIs are assumed to bind to the variable `?id`.
            * @param {string} resultSet Constraints that result in the URIs of
            *   the resources to page. The URIs should be bound as `?id`.
            * @param {string} [orderBy] A SPARQL expression that can be used to
            *   order the results. Default is '?id'.
            * @returns {Object} a query object with the following properties:
            *
            *   - **query** - `{string}` - The constructed SPARQL queryTemplate (with a `<PAGE>` placeholder for paging).
            *   - **resultSetQry** - `{string}` - The result set query.
            * @example
            * <pre>
            * var resultSet = '?id a <http://dbpedia.org/ontology/Writer> .';
            *
            * var queryTemplate =
            * 'SELECT * WHERE { ' +
            * ' <RESULT_SET> ' +
            * ' OPTIONAL { ?id rdfs:label ?label . } ' +
            * '}';
            *
            * var qryObj = queryBuilder.buildQuery(qry, resultSet, '?id');
            *
            * // qryObj.query returns (without line breaks):
            * // PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            * // PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            * // SELECT * WHERE {
            * //   {
            * //     SELECT DISTINCT ?id {
            * //       ?id a <http://dbpedia.org/ontology/Writer>.
            * //     } ORDER BY ?id <PAGE>
            * //   }
            * //   OPTIONAL { ?id rdfs:label ?label . }
            * // }
            *
            * // qryObj.resultSetQry returns (without line breaks):
            * // PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            * // PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            * // SELECT DISTINCT ?id {
            * //   ?id a <http://dbpedia.org/ontology/Writer>.
            * // } ORDER BY ?id <PAGE>
            * </pre>
            */
            function buildQuery(queryTemplate, resultSet, orderBy) {
                var resultSetQry = resultSetQryShell
                    .replace('<CONTENT>', resultSet)
                    .replace('<ORDER_BY>', orderBy || '?id');

                var resultSetPart = resultSetShell
                    .replace('<RESULT_SET>', resultSetQry);

                resultSetQry = prefixes + resultSetQry;

                var query = prefixes + queryTemplate.replace('<RESULT_SET>', resultSetPart);

                return {
                    resultSetQuery: resultSetQry,
                    query: query
                };
            }
        }
    }
})();
