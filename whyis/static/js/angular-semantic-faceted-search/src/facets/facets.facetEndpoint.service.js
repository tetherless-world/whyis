(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .service('facetEndpoint', facetEndpoint);

    /* @ngInject */
    function facetEndpoint(AdvancedSparqlService, facetMapperService) {

        this.getEndpoint = getEndpoint;

        function getEndpoint(config) {
            var endpointConfig = {
                endpointUrl: config.endpointUrl,
                usePost: config.usePost,
                headers: config.headers
            };
            return new AdvancedSparqlService(endpointConfig, config.mapper || facetMapperService);
        }
    }
})();
