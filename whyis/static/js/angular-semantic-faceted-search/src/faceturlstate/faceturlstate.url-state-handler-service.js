(function() {

    'use strict';

    /* eslint-disable angular/no-service-method */
    angular.module('seco.facetedSearch')

    /**
    * @ngdoc service
    * @name seco.facetedSearch.facetUrlStateHandlerService
    * @description
    * # facetUrlStateHandlerService
    * Service for updating the URL parameters based on facet selections,
    * and retrieving the facet values from URL parameters.
    *
    * Intended for bookmarking the current facet selections.
    * {@link seco.facetedSearch.FacetHandler `FacetHandler`} can take
    * the return value of `getFacetValuesFromUrlParams` as the
    * `initialState` configuration value.
    *
    * Updating the URL parameters can be done, e.g., when the facet states
    * have been received while listening for facet updates.
    * See {@link seco.facetedSearch.FacetHandler `FacetHandler`} for details
    * regarding events.
    */
    .service('facetUrlStateHandlerService', facetUrlStateHandlerService);

    /* @ngInject */
    function facetUrlStateHandlerService($location, _) {

        this.updateUrlParams = updateUrlParams;
        this.getFacetValuesFromUrlParams = getFacetValuesFromUrlParams;

        /**
        * @ngdoc method
        * @methodOf seco.facetedSearch.facetUrlStateHandlerService
        * @name seco.facetedSearch.facetUrlStateHandlerService#updateUrlParams
        * @description
        * Update the URL parameters based on the given facet state.
        * @param {Object} facets The facet states as broadcast by
        *   {@link seco.facetedSearch.FacetHandler `FacetHandler`}.
        */
        function updateUrlParams(facets) {
            facets = facets.facets || facets;
            var params = {};
            _(facets).forOwn(function(val, id) {
                if (val && val.value && !(_.isObject(val.value) && _.isEmpty(val.value))) {
                    params[id] = { value: val.value, constraint: val.constraint };
                }
            });
            if (_.isEmpty(params)) {
                params = null;
            } else {
                params = angular.toJson(params);
            }
            $location.search('facets', params);
        }

        /**
        * @ngdoc method
        * @methodOf seco.facetedSearch.facetUrlStateHandlerService
        * @name seco.facetedSearch.facetUrlStateHandlerService#getFacetValuesFromUrlParams
        * @description
        * Get the facet states from the URL parameters.
        * @return {Object} The facet states.
        */
        function getFacetValuesFromUrlParams() {
            var res = {};

            var params = ($location.search() || {}).facets;
            if (!params) {
                return res;
            }
            try {
                params = angular.fromJson(params);
            }
            catch(e) {
                $location.search('facets', null);
                return res;
            }
            _.forOwn(params, function(val, id) {
                res[id] = val;
            });
            return res;
        }
    }
})();
