(function() {
    'use strict';

    /**
    * @ngdoc directive
    * @name seco.facetedSearch.directive:secoCheckboxFacet
    * @restrict 'E'
    * @element ANY
    * @description
    * A facet for a checkbox selector based on a triple pattern.
    *
    * If multiple checkboxes are selected, the resulting SPARQL constraint
    * will be a union of the selections.
    *
    * @param {Object} options The configuration object with the following structure:
    * - **facetId** - `{string}` - A friendly id for the facet.
    *   Should be unique in the set of facets, and should be usable as a SPARQL variable.
    * - **name** - `{string}` - The title of the facet. Will be displayed to end users.
    * - **choices** - `{Array}` - A list of choices and their definitions.
    *   Each element in the list should be an object:
    *   `{ id: 'uniqueIdForThisChoice', pattern: '[SPARQL pattern]', label: 'choice label' }`.
    *   `[SPARQL pattern]` is any SPARQL pattern where `?id` is the variable bound to the
    *   result resource. Example:
    *       {
    *         id: 'hobby',
    *         pattern: '?id <http://schema.org/hobby> [] .',
    *         label: 'Hobby'
    *       }
    *   This would create a checkbox which would restrict the results to those
    *   resources that have a value for the property `<http://schema.org/hobby>`.
    * - **[enabled]** `{boolean}` - Whether or not the facet is enabled by default.
    *   If undefined, the facet will be disabled by default.
    * - **[endpointUrl]** `{string}` - The URL of the SPARQL endpoint.
    *   Optional, as it can also be given globally in
    *   {@link seco.facetedSearch.FacetHandler `FacetHandler`} config.
    * - **[chart]** `{boolean}` - If truthy, there will be an additional button next to the
    *   enable/disable button of the facet. Clicking the button will display the facet values
    *   as a pie chart.
    * - **[headers]** `{Object}` - Additional HTTP headers.
    * - **[priority]** - `{number}` - Priority for constraint sorting.
    *   Undefined by default.
    */
    angular.module('seco.facetedSearch')
    .directive('secoCheckboxFacet', checkboxFacet);

    function checkboxFacet() {
        return {
            restrict: 'E',
            scope: {
                options: '='
            },
            controller: 'CheckboxFacetController',
            controllerAs: 'vm',
            templateUrl: 'src/facets/checkbox/facets.checkbox-facet.directive.html'
        };
    }
})();
