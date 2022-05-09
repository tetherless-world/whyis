(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoTimespanFacet
    * @restrict 'E'
    * @element ANY
    * @description
    * A facet for selecting date ranges.
    *
    * Restricts the selectable dates by getting the minimum and maximum dates
    * based on the underlying data, and facet selections.
    *
    * Currently only supports values of the type <http://www.w3.org/2001/XMLSchema#date>,
    * and there is no support for timezones. Any timezones in the values retrieved
    * will be discarded.
    *
    * @param {Object} options The configuration object with the following structure:
    * - **facetId** - `{string}` - A friendly id for the facet.
    *   Should be unique in the set of facets, and should be usable as a SPARQL variable.
    * - **name** - `{string}` - The title of the facet. Will be displayed to end users.
    * - **startPredicate** - `{string}` - The predicate or property path that defines
    *   the start date of the date range.
    * - **endPredicate** - `{string}` - The predicate or property path that defines
    *   the end date of the date range.
    * - **[min]** - `{string|Date}` - The earliest selectable date. If string, should
    *   be in ISO format. Giving a Date object that has a predefined timezone other
    *   than the user's may lead to timezone issues.
    * - **[max]** - `{string|Date}` - The earliest selectable date. If string, should
    *   be in ISO format. Giving a Date object that has a predefined timezone other
    *   than the user's may lead to timezone issues.
    * - **[enabled]** `{boolean}` - Whether or not the facet is enabled by default.
    *   If undefined, the facet will be disabled by default.
    * - **[endpointUrl]** `{string}` - The URL of the SPARQL endpoint.
    *   Optional, as it can also be given globally in
    *   {@link seco.facetedSearch.FacetHandler `FacetHandler`} config.
    * - **[headers]** `{Object}` - Additional HTTP headers.
    * - **[priority]** - `{number}` - Priority for constraint sorting.
    *   Undefined by default.
    */
    angular.module('seco.facetedSearch')
    .directive('secoTimespanFacet', timespanFacet);

    function timespanFacet() {
        return {
            restrict: 'E',
            scope: {
                options: '='
            },
            controller: 'TimespanFacetController',
            controllerAs: 'vm',
            templateUrl: 'src/facets/timespan/facets.timespan-facet.directive.html'
        };
    }
})();
