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

(function() {
    'use strict';

    /* eslint-disable angular/no-service-method */

    /**
    * @ngdoc service
    * @name sparql.objectMapperService
    * @description
    * Service for transforming SPARQL results into more manageable objects.
    *
    * The service can be extended via prototype inheritance by re-implementing
    * any of the methods. The most likely candidates for re-implementation are
    * `makeObject`, `reviseObject`, and `postProcess`.
    *
    * The methods for using the service are `makeObjectList`, and `makeObjectListNoGrouping`.
    */
    angular.module('sparql')
    .service('objectMapperService', objectMapperService);

    /* ngInject */
    function objectMapperService(_) {
        /* Overridable processing methods */
        ObjectMapper.prototype.makeObject = makeObject;
        ObjectMapper.prototype.reviseObject = reviseObject;
        ObjectMapper.prototype.mergeObjects = mergeObjects;
        ObjectMapper.prototype.mergeValueToList = mergeValueToList;
        ObjectMapper.prototype.postProcess = postProcess;

        /* API methods */
        ObjectMapper.prototype.makeObjectList = makeObjectList;
        ObjectMapper.prototype.makeObjectListNoGrouping = makeObjectListNoGrouping;

        return new ObjectMapper();

        function ObjectMapper() {
            this.objectClass = Object;
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#makeObjectList
        * @param {Array} objects A list of objects as SPARQL results.
        * @returns {Array} The mapped object list.
        * @description
        * Map the SPARQL results as objects, and return a list where result rows with the same
        * id are merged into one object.
        */
        function makeObjectList(objects) {
            var self = this;
            var objList = _.transform(objects, function(result, obj) {
                if (!obj.id) {
                    return null;
                }
                var orig = obj;
                obj = self.makeObject(obj);
                obj = self.reviseObject(obj, orig);
                self.mergeValueToList(result, obj);
            });
            return self.postProcess(objList);
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#makeObjectListNoGrouping
        * @param {Array} objects A list of objects as SPARQL results.
        * @returns {Array} The mapped object list.
        * @description
        * Maps the SPARQL results as objects, but does not merge any rows.
        */
        function makeObjectListNoGrouping(objects) {
            // Create a list of the SPARQL results where each result row is treated
            // as a separated object.
            var self = this;
            var obj_list = _.transform(objects, function(result, obj) {
                obj = self.makeObject(obj);
                result.push(obj);
            });
            return obj_list;
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#makeObject
        * @param {Object} obj A single SPARQL result row object.
        * @returns {Object} The mapped object.
        * @description
        * Flatten the result object. Discard everything except values.
        * Assume that each property of the obj has a value property with
        * the actual value.
        */
        function makeObject(obj) {
            var o = new this.objectClass();

            _.forIn(obj, function(value, key) {
                // If the variable name contains "__", an object
                // will be created as the value
                // E.g. { place__id: '1' } -> { place: { id: '1' } }
                _.set(o, key.replace(/__/g, '.'), value.value);
            });

            return o;
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#reviseObject
        * @param {Object} obj A single object as returned by {@link sparql.objectMapperService#makeObject makeObject}.
        * @param {Object} original A single SPARQL result row object.
        * @returns {Object} The revised object.
        * @description
        * Provides a hook for revising an object after it has been processed by {@link sparql.objectMapperService#makeObject makeObject}.
        * The defaul implementation is a no-op.
        */
        function reviseObject(obj, original) { // eslint-disable-line no-unused-vars
            // This is called with a reference to the original result objects
            // as the second parameter.
            return obj;
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#mergeValueToList
        * @param {Array} valueList A list to which the value should be added.
        * @param {Object} value The value to add to the list.
        * @returns {Array} The merged list.
        * @description
        * Add the given value to the given list, merging an object value to and
        * object in the list if both have the same id attribute.
        * A value already present in valueList is discarded.
        */
        function mergeValueToList(valueList, value) {
            var old;
            if (_.isObject(value) && value.id) {
                // Check if this object has been constructed earlier
                old = _.findLast(valueList, function(e) {
                    return e.id === value.id;
                });
                if (old) {
                    // Merge this object to the object constructed earlier
                    this.mergeObjects(old, value);
                }
            } else {
                // Check if this value is present in the list
                old = _.findLast(valueList, function(e) {
                    return _.isEqual(e, value);
                });
            }
            if (!old) {
                // This is a distinct value
                valueList.push(value);
            }
            return valueList;
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#mergeObjects
        * @param {Object} first An object as returned by {@link sparql.objectMapperService#makeObject makeObject}.
        * @param {Object} second The object to merge with the first.
        * @returns {Object} The merged object.
        * @description
        * Merges two objects.
        */
        function mergeObjects(first, second) {
            // Merge two objects into one object.
            return _.mergeWith(first, second, merger.bind(this));
        }

        function merger(a, b) {
            var self = this;
            if (_.isEqual(a, b)) {
                return a;
            }
            if (a && !b) {
                return a;
            }
            if (b && !a) {
                return b;
            }
            if (_.isArray(a)) {
                if (_.isArray(b)) {
                    b.forEach(function(bVal) {
                        return self.mergeValueToList(a, bVal);
                    });
                    return a;
                }
                return self.mergeValueToList(a, b);
            }
            if (_.isArray(b)) {
                return self.mergeValueToList(b, a);
            }
            if (!(_.isObject(a) && _.isObject(b) && a.id === b.id)) {
                return [a, b];
            }
            return self.mergeObjects(a, b);
        }

        /**
        * @ngdoc method
        * @methodOf sparql.objectMapperService
        * @name sparql.objectMapperService#postProcess
        * @param {Array} objects A list of mapped objects.
        * @returns {Array} The processed object list.
        * @description
        * Provides a hook for processing the object list after all results have been processed.
        * The defaul implementation is a no-op.
        */
        function postProcess(objects) {
            return objects;
        }
    }
})();

(function() {

    'use strict';

    /**
    * @ngdoc object
    * @name sparql.PagerService
    */
    angular.module('sparql')
    .factory('PagerService', PagerService);

    /* ngInject */
    function PagerService($q, _) {

        /**
        * @ngdoc function
        * @name sparql.PagerService
        * @constructor
        * @description
        * Service for paging SPARQL results.
        *
        * {@link sparql.AdvancedSparqlService `AdvancedSparqlService`} initializes this service, so manual init is not needed.
        * @param {string} sparqlQry The SPARQL query.
        * @param {string} resultSetQry The result set subquery part of the query - i.e. the part which
        * defines the distinct objects that are being paged
        * (containing `<PAGE>` as a placeholder for SPARQL limit and offset).
        * @param {number} itemsPerPage The size of a single page.
        * @param {function} getResults A function that returns a promise of results given a
        * SPARQL query.
        * @param {number} [pagesPerQuery=1] The number of pages to get per query.
        * @param {number} [itemCount] The total number of items that the sparqlQry returns.
        * Optional, will be queried based on the resultSetQry if not given.
        */
        return function(sparqlQry, resultSetQry, itemsPerPage, getResults, pagesPerQuery, itemCount) {

            var self = this;

            /* Public API */

            // getTotalCount() -> promise
            self.getTotalCount = getTotalCount;
            // getMaxPageNo() -> promise
            self.getMaxPageNo = getMaxPageNo;
            // getPage(pageNumber) -> promise
            self.getPage = getPage;
            // getAll() -> promise
            self.getAll = getAll;
            // getAllSequentially(chunkSize) -> promise
            self.getAllSequentially = getAllSequentially;

            // How many pages to get with one query.
            self.pagesPerQuery = pagesPerQuery || 1;

            /* Internal vars */

            // The total number of items.
            var count = undefined;
            if (angular.isDefined(itemCount)) {
                count = $q.defer();
                count.resolve(itemCount);
            }
            // The number of the last page.
            var maxPage = itemCount ? calculateMaxPage(itemCount, pageSize) : undefined;
            // Cached pages.
            var pages = [];

            var pageSize = itemsPerPage;

            var countQry = countify(resultSetQry.replace('<PAGE>', ''));

            /* Public API function definitions */

            /**
            * @ngdoc method
            * @methodOf sparql.PagerService
            * @name sparql.PagerService#getPage
            * @description
            * Get a specific "page" of data.
            * @param {string} pageNo The number of the page to get (0-indexed).
            * @param {number} [size] The page size. Changes the configured page size.
            *   Using this parameter is not recommended, and may be removed in the future.
            * @returns {promise} A promise of the page of the query results as objects.
            */
            function getPage(pageNo, size) {
                /*
                * TODO: Fix race condition problem when changing the page size (perhaps don't
                *      allow it at all without a new instantiation?)
                */
                // Currently prone to race conditions when using the size
                // parameter to change the page size.

                if (size && size !== pageSize) {
                    // Page size change. Clear page cache.
                    // This part is problematic if the function is called
                    // multiple times in short succession.
                    pageSize = size;
                    pages = [];
                }

                // Get cached page if available.
                if (pages[pageNo]) {
                    return pages[pageNo].promise;
                }
                if (pageNo < 0) {
                    return $q.when([]);
                }
                return getTotalCount().then(function(count) {
                    if (pageNo > maxPage || !count) {
                        return $q.when([]);
                    }
                    // Get the page window for the query (i.e. query for surrounding
                    // pages as well according to self.pagesPerQuery).
                    var start = getPageWindowStart(pageNo);
                    // Assign a promise to each page within the window as all of those
                    // will be fetched.
                    for (var i = start; i < start + self.pagesPerQuery && i <= maxPage; i++) {
                        if (!pages[i]) {
                            pages[i] = $q.defer();
                        }
                    }
                    // Query for the pages.
                    return getResults(pagify(sparqlQry, start, pageSize, self.pagesPerQuery))
                    .then(function(results) {
                        var chunks = _.chunk(results, pageSize);
                        chunks.forEach(function(page) {
                            // Resolve each page promise.
                            pages[start].resolve(page);
                            start++;
                        });
                        // Return (the promise of) the requested page.
                        return pages[pageNo].promise;
                    });
                });
            }

            /**
            * @ngdoc method
            * @methodOf sparql.PagerService
            * @name sparql.PagerService#getAllSequentially
            * @description
            * Get all results sequentially in chunks.
            * @param {number} chunkSize The amount of results to get per query.
            * @returns {promise} A promise of the query results as objects.
            * The promise will be notified between receiving chunks.
            */
            function getAllSequentially(chunkSize) {
                var all = [];
                var res = $q.defer();
                var chain = $q.when();
                return getTotalCount().then(function(count) {
                    var max = Math.ceil(count / chunkSize);
                    var j = 0;
                    for (var i = 0; i < max; i++) {
                        chain = chain.then(function() {
                            return getResults(pagify(sparqlQry, j++, chunkSize, 1)).then(function(page) {
                                all = all.concat(page);
                                res.notify(all);
                            });
                        });
                    }
                    chain.then(function() {
                        fillPages(all);
                        res.resolve(all);
                    });

                    return res.promise;
                });
            }

            /**
            * @ngdoc method
            * @methodOf sparql.PagerService
            * @name sparql.PagerService#getAll
            * @description
            * Get all results.
            * @returns {promise} A promise of the query results as objects.
            */
            function getAll() {
                return getResults(pagify(sparqlQry, 0, 0)).then(function(results) {
                    fillPages(results);
                    return results;
                });
            }

            /**
            * @ngdoc method
            * @methodOf sparql.PagerService
            * @name sparql.PagerService#getTotalCount
            * @description
            * Get the total count of results.
            * @returns {promise} A promise of total count of the query results.
            */
            function getTotalCount() {
                if (angular.isDefined(count)) {
                    return count.promise.then(function(value) {
                        maxPage = calculateMaxPage(value, pageSize);
                        return value;
                    });
                }
                count = $q.defer();
                return getResults(countQry, true).then(function(results) {
                    var value = parseInt(results[0].count.value);
                    count.resolve(value);
                    maxPage = calculateMaxPage(value, pageSize);
                    return value;
                });
            }

            /**
            * @ngdoc method
            * @methodOf sparql.PagerService
            * @name sparql.PagerService#getMaxPageNo
            * @description
            * Get the number of the last page of results.
            * @returns {promise} A promise of the number of the last page.
            */
            function getMaxPageNo() {
                return getTotalCount().then(function(count) {
                    return calculateMaxPage(count, pageSize);
                });
            }

            /* Internal helper functions */

            function fillPages(results) {
                pages = _.map(_.chunk(results, pageSize), function(res) {
                    var promise = $q.defer();
                    promise.resolve(res);
                    return promise;
                });
                if (angular.isUndefined(count)) {
                    count = $q.defer();
                }
                count.resolve(results.length);
            }

            function pagify(sparqlQry, page, pageSize, pagesPerQuery) {
                // Form the query for the given page.
                if (pageSize === 0) {
                    return sparqlQry.replace('<PAGE>', '');
                } else {
                    return sparqlQry.replace('<PAGE>',
                        ' LIMIT ' + pageSize * pagesPerQuery + ' OFFSET ' + (page * pageSize));
                }
            }

            function countify(sparqlQry) {
                // Form a query that counts the total number of items returned
                // by the query (by replacing the first SELECT with a COUNT).
                return sparqlQry.replace(/(\bselect\b.+?(where)?\W+?\{)/i,
                    'SELECT (COUNT(DISTINCT ?id) AS ?count) WHERE { $1 ') + ' }';
            }

            function getPageWindowStart(pageNo) {
                // Get the page number of the first page to fetch.

                if (pageNo <= 0) {
                    // First page.
                    return 0;
                }
                if (pageNo >= maxPage) {
                    // Last page -> window ends on last page.
                    return Math.max(pageNo - self.pagesPerQuery + 1, 0);
                }
                var minMin = pageNo < self.pagesPerQuery ? 0 : pageNo - self.pagesPerQuery;
                var maxMax = pageNo + self.pagesPerQuery > maxPage ? maxPage : pageNo + self.pagesPerQuery;
                var min, max;
                for (min = minMin; min <= pageNo; min++) {
                    // Get the lowest non-cached page within the extended window.
                    if (!pages[min]) {
                        break;
                    }
                }
                if (min === pageNo) {
                    // No non-cached pages before the requested page within the extended window.
                    return pageNo;
                }
                for (max = maxMax; max > pageNo; max--) {
                    // Get the highest non-cached page within the extended window.
                    if (!pages[max]) {
                        break;
                    }
                }
                if (minMin === min && maxMax === max) {
                    // No cached pages near the requested page
                    // -> requested page in the center of the window
                    return min + Math.ceil(self.pagesPerQuery / 2);
                }
                if (max < maxMax) {
                    // There are some cached pages toward the end of the extended window
                    // -> window ends at the last non-cached page
                    return Math.max(max - self.pagesPerQuery + 1, 0);
                }
                // Otherwise window starts from the lowest non-cached page
                // within the extended window.
                return min;
            }

            function calculateMaxPage(count, pageSize) {
                return Math.ceil(count / pageSize) - 1;
            }

        };
    }
})();

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
