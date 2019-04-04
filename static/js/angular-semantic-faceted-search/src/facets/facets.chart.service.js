(function() {
    'use strict';

    angular.module('seco.facetedSearch')
    .factory('FacetChartService', FacetChartService);

    /* @ngInject */
    function FacetChartService(_) {

        return FacetChartService;

        function FacetChartService(config) {
            var self = this;

            self.scope = config.scope;
            self.facet = config.facet;

            self.handleChartClick = handleChartClick;
            self.updateChartData = updateChartData;
            self.clearChartData = clearChartData;

            self.scope.$on('chart-create', function(evt, chart) {
                // Highlight the selected value on init
                updateChartHighlight(chart, self.facet.getSelectedValue());
            });

            function clearChartData() {
                self.chartData = {
                    values: [],
                    data: [],
                    labels: []
                };
            }

            function updateChartData() {
                self.clearChartData();
                if (self.facet.getState) {
                    self.facet.getState().forEach(function(val) {
                        // Don't add "no selection"
                        if (angular.isDefined(val.value)) {
                            self.chartData.values.push(val.value);
                            self.chartData.data.push(val.count);
                            self.chartData.labels.push(val.text);
                        }
                    });
                }
            }

            function clearChartSliceHighlight(chartElement, updateChart) {
                _.set(chartElement.custom, 'backgroundColor', null);
                _.set(chartElement.custom, 'borderWidth', null);
                if (updateChart) {
                    chartElement._chart.update();
                }
            }

            function highlightChartElement(chartElement, updateChart) {
                _.set(chartElement, 'custom.backgroundColor', 'grey');
                chartElement.custom.borderWidth = 10;
                if (updateChart) {
                    chartElement._chart.update();
                }
            }

            function updateChartHighlight(chart, values) {
                var chartElements = chart.getDatasetMeta(0).data;
                // Clear previous selection
                chartElements.forEach(function(elem) {
                    clearChartSliceHighlight(elem);
                });

                values = _.compact(_.castArray(values));
                values.forEach(function(value) {
                    var index = _.indexOf(self.chartData.values, value);
                    var chartElement = _.find(chartElements, ['_index', index]);
                    highlightChartElement(chartElement);
                });

                chart.update();
            }

            function updateChartSelection(chartElement) {
                var selectedValue = self.chartData.values[chartElement._index];

                if (_.get(chartElement, 'custom.backgroundColor')) {
                    // Slice was already selected, so clear the selection
                    clearChartSliceHighlight(chartElement, true);
                    self.facet.deselectValue(selectedValue);
                    return self.facet.getSelectedValue();
                }

                self.facet.setSelectedValue(selectedValue);

                updateChartHighlight(chartElement._chart, self.facet.getSelectedValue());

                return self.facet.getSelectedValue();
            }

            function handleChartClick(chartElement) {
                return updateChartSelection(chartElement[0]);
            }
        }
    }
})();
