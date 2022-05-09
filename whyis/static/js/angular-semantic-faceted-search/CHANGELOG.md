# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/),
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.11.0] - 2018-05-18

### Added

- Configuration option for displaying facets as pie charts. If the option `chart` is truthy,
  the user can click a button next to the disable facet button to see and interact with the
  facet as a pie chart. The option is applicable for
  [BasicFacet](http://semanticcomputing.github.io/angular-semantic-faceted-search/#/api/seco.facetedSearch.directive:secoBasicFacet)
  and [CheckboxFacet](http://semanticcomputing.github.io/angular-semantic-faceted-search/#/api/seco.facetedSearch.directive:secoCheckboxFacet).
  It also works with
  [HierachyFacet](http://semanticcomputing.github.io/angular-semantic-faceted-search/#/api/seco.facetedSearch.directive:secoHierarchyFacet),
  but the hierarchy is not visualized, so usage with that facet is not recommended.
  The option is disabled by default.

## [1.10.0] - 2018-03-13

### Changed

- Cosmetic changes:
    - Facet disable button is now more subtle.
    - The enable/disable button is consistently placed.
    - Loading spinner is smaller.
- Refactored facet templates (this has some DOM/CSS implications).

## [1.9.1] - 2017-11-28

### Fixed

- Disabling and enabling a facet now works, instead of leaving the facet
  unresponsive.

## [1.9.0] - 2017-11-27

### Changed

- When an error occurs, don't try to display the error message to the user.

## [1.8.1] - 2017-10-16

### Changed

- Optimize hierarchy facet constraint.

## [1.8.0] - 2017-09-14

### Changed

- Add configuration option for HTTP headers.

## [1.7.2] - 2017-08-07

### Fixed

- Make the `priority` option work.

## [1.7.1] - 2017-08-03

### Changed

- Hierarchical facet now supports the `specifier` option.
- Hierarchical facet now displays only one dash per level in the hierarchy.

## [1.7.0] - 2017-07-26

### Changed

- Hierarchical facet now supports multiple levels in the hierarchy.
  The `classes` option is no longer needed.

## [1.6.1] - 2017-07-24

### Changed

- Update angular-spinner dependency.

## [1.6.0] - 2017-07-14

### Changed

- Make release version safe for minification.

## [1.5.4] - 2017-07-11

### Fixed

- Hierarchical facet now always shows all values.

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

[Unreleased]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.11.0...HEAD
[1.11.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.10.0...1.11.0
[1.10.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.9.1...1.10.0
[1.9.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.9.0...1.9.1
[1.9.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.8.1...1.9.0
[1.8.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.8.0...1.8.1
[1.8.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.7.1...1.8.0
[1.7.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.7.0...1.7.1
[1.7.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.6.1...1.7.0
[1.6.1]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.6.0...1.6.1
[1.6.0]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.4...1.6.0
[1.5.4]: https://github.com/SemanticComputing/angular-semantic-faceted-search/compare/1.5.3...1.5.4
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
