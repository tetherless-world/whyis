/* eslint-disable */
module.exports = function(config) {
    config.set({
        frameworks: ['jasmine'],
    files: [
        '../bower_components/angular/angular.js',
        '../bower_components/angular-mocks/angular-mocks.js',
        '../bower_components/lodash/lodash.js',
        '../bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
        '../bower_components/angular-paging-sparql-service/dist/sparql-service.js',
        '../bower_components/spin.js/spin.js',
        '../bower_components/angular-spinner/dist/angular-spinner.js',
        '../bower_components/checklist-model/checklist-model.js',
        '../bower_components/chart.js/dist/Chart.js',
        '../bower_components/angular-chart.js/angular-chart.js',
        '../src/facets/facets.module.js',
        '../src/**/*.js',
        '*.js'
        ]
    })
}
