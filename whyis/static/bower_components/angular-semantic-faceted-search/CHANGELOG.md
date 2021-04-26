# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/),
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.5.3] - 2017-05-02

### Fixed

- FacetResultHandler now works without paging.

## [1.5.2] - 2017-03-27

### Fixed

- Queries to additional endpoints now return labels for values.

## [1.5.1] - 2017-03-24

### Fixed

- Timespan facet does not break anymore if its query returns undefined dates.

## [1.5.0] - 2017-03-15

### Added

- Checkbox facet (secoCheckboxFacet)

### Changed

- Simplified facet state update
- BasicFacet no longer does federated queries - a separate query for each
  service is produced instead.
- Multiple languages can now be given as the `preferredLang`.

## [1.4.1] - 2017-01-16

### Changed
- Values for the timespan facet are now cast as xsd:date in SPARQL

### Fixed
- Fix timespan facet date limits when selection changes

## [1.4.0] - 2017-01-11

### Changed
- Selecting a value in a basic facet does not update the list of selections anymore.
  This way the user can change the selection without clearing the selection first.
- Facet selections should now work with all literal datatypes.

## [1.3.2] - 2016-12-15

### Fixed
- Timespan facet selections restrictions fixed.

## [1.3.1] - 2016-11-15

### Fixed
- Sanitize the user's query in secoJenaTextFacet to avoid syntax errors from the
  SPARQL endpoint.

## [1.3.0] - 2016-11-15

### Changed
- secoJenaTextFacet allows for more user control in the search.
  I.e. it does not modify the user input except for excaping quotes
  (and removing them if they are unbalanced)
- secoJenaTextFacet default priority is now 0 (instead of 10).

## [1.2.1] - 2016-11-15

### Added
- `limit` and `graph` configuration options for secoJenaTextFacet.

## [1.2.0] - 2016-11-14

### Added
- [secoJenaTextFacet](http://semanticcomputing.github.io/angular-semantic-faceted-search/#/api/seco.facetedSearch.directive:secoJenaTextFacet)
- `priority` configuration variable to provide a way to sort the facet constraints (see the [documentation][api]).


## [1.1.1] - 2016-11-04

### Fixed
- Dates are hard. Dates should now appear the same in queries, URL params,
  and in the date picker, regardless of the user's timezone.

## [1.1.0] - 2016-11-03

### Changed
- Timespan facet now works as an actual facet by querying for minimum and maximum
  available dates, and adjusts the datepicker max and min dates accordingly.

## [1.0.7] - 2016-11-03

### Fixed
- Fix setting the timespan face's initial values.
- Fix an issue with the timespan facet where the selected date could be different
  from the one actually used in the query.

## [1.0.6] - 2016-11-02

### Added
- Changelog

### Changed
- UI Bootstrap dependency updated to ^2.2.0

### Fixed
- Fix the timespan facet, and its documentation

[Unreleased]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.2...HEAD
[1.5.3]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.2...1.5.3
[1.5.2]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.1...1.5.2
[1.5.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.0...1.5.1
[1.5.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.4.1...1.5.0
[1.4.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.3.2...1.4.0
[1.3.2]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.3.1...1.3.2
[1.3.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.3.0...1.3.1
[1.3.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.2.1...1.3.0
[1.2.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.1.1...1.2.0
[1.1.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.0.7...1.1.1
[1.1.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.0.7...1.1.0
[1.0.7]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.0.6...1.0.7
[1.0.6]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.0.5...1.0.6
[api]: http://semanticcomputing.github.io/angular-semantic-faceted-search/#/api
