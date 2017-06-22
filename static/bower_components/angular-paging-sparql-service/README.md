# Angular SPARQL service with paging and object mapping

Angular service for querying SPARQL endpoints, and mapping the results
as simple objects.

## Installation

`bower install angular-paging-sparql-service`

Include `sparql` in your module dependenies:

```
angular.module('myApp', ['sparql'])
```

## Usage

See the [documentation](http://semanticcomputing.github.io/angular-paging-sparql-service/#/api).

Example projects using the module:

* [SPARQL Faceter DBpedia demo](https://github.com/SemanticComputing/sparql-faceter-dbpedia-demo)
* [WarSampo death records](https://github.com/SemanticComputing/WarSampo-death-records)

## Development

Requires
[Karma](https://karma-runner.github.io/), and [Grunt](http://gruntjs.com/).

Install dev dependenies

`npm install`

### Running tests

`karma start`

### Building

`grunt build`
