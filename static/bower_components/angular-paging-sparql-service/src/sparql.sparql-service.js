(function() {
    'use strict';

    /* eslint-disable angular/no-service-method */

    /**
    * @ngdoc object
    * @name sparql.SparqlService
    */
    angular.module('sparql')
    .factory('SparqlService', SparqlService);

    /**
    * @ngdoc function
    * @name sparql.SparqlService
    * @constructor
    * @description
    * Service for querying a SPARQL endpoint.
    * @param {Object|string} configuration object or the SPARQL endpoit URL as a string.
    *   The object has the following properties:
    *
    *   - **endpointUrl** - `{string}` - The SPARQL endpoint URL.
    *   - **usePost** - `{boolean}` - If truthy, use POST instead of GET. Default is `false`.
    * @example
    * <pre>
    * var endpoint = new SparqlService({ endpointUrl: 'http://dbpedia.org/sparql', usePost: false });
    * // Or using just a string parameter:
    * endpoint = new SparqlService('http://dbpedia.org/sparql');
    *
    * var qry =
    * 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ';
    * 'SELECT * WHERE { ' +
    * ' ?id a <http://dbpedia.org/ontology/Writer> . ' +
    * ' OPTIONAL { ?id rdfs:label ?label . } ' +
    * '}';
    *
    * var resultPromise = endpoint.getObjects(qry);
    * </pre>
    */
    /* ngInject */
    function SparqlService($http, $q, _) {
        return function(configuration) {

            if (_.isString(configuration)) {
                // Backwards compatibility
                configuration = { endpointUrl: configuration };
            }

            var defaultConfig = { usePost: false };

            var config = angular.extend({}, defaultConfig, configuration);

            var executeQuery = config.usePost ? post : get;

            function get(qry) {
                return $http.get(config.endpointUrl + '?query=' + encodeURIComponent(qry) + '&format=json');
            }

            function post(qry) {
                var data = 'query=' + encodeURIComponent(qry);
                var conf = { headers: {
                    'Accept': 'application/sparql-results+json',
                    'Content-type' : 'application/x-www-form-urlencoded'
                } };
                return $http.post(config.endpointUrl, data, conf);
            }

            /**
            * @ngdoc method
            * @methodOf sparql.SparqlService
            * @name sparql.SparqlService#getObjects
            * @param {string} sparqlQry The SPARQL query.
            * @returns {promise} A promise of the SPARQL results.
            * @description
            * Get the SPARQL query results as a list of objects.
            * @example
            * <pre>
            * var resultPromise = endpoint.getObjects(qry);
            * </pre>
            */
            function getObjects(sparqlQry) {
                // Query the endpoint and return a promise of the bindings.
                return executeQuery(sparqlQry).then(function(response) {
                    return response.data.results.bindings;
                }, function(response) {
                    return $q.reject(response.data);
                });
            }

            return {
                getObjects: getObjects
            };
        };
    }
})();
