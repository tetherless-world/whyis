# Angular to Vue.js Migration Guide

## Overview

This document tracks the migration of Angular.js code from `whyis/static/js/whyis.js` to Vue.js components in the `whyis/static/js/whyis_vue/` directory.

## Migration Status

### ✅ CORE MIGRATION COMPLETE

All high-priority Angular.js components have been successfully migrated to Vue.js with comprehensive test coverage.

### Completed Migrations

#### Utilities (whyis_vue/utilities/)

1. **url-utils.js** - URL and data URI handling utilities
   - `getParameterByName()` - Extract query parameters from URLs
   - `decodeDataURI()` - Decode data URIs with UTF-8 support
   - `encodeDataURI()` - Encode strings/buffers as data URIs
   - Migrated from: Global functions in whyis.js (lines 5-97)
   - Tests: tests/utilities/url-utils.spec.js (23 tests)

2. **label-fetcher.js** - Resource label fetching with caching
   - `getLabel()` - Async label fetching with automatic caching
   - `getLabelSync()` - Synchronous cache access
   - `labelFilter` - Vue filter for reactive label display
   - `clearLabelCache()`, `hasLabel()` - Cache management
   - Migrated from: Angular factory "getLabel" (lines 959-992)
   - Tests: tests/utilities/label-fetcher.spec.js (16 tests)

3. **formats.js** - RDF and semantic data format definitions
   - `getFormatByExtension()` - Lookup format by file extension
   - `getFormatByMimetype()` - Lookup format by MIME type
   - `getFormatFromFilename()` - Extract format from filename
   - `isFormatSupported()` - Check if format is supported
   - Migrated from: Angular factory "formats" (lines 752-776)
   - Tests: tests/utilities/formats.spec.js (29 tests)

4. **resolve-entity.js** - Entity resolution for search/autocomplete
   - `resolveEntity()` - Search and resolve entities by query
   - Supports type filtering and wildcard search
   - Migrated from: Angular service "resolveEntity" (lines 1391-1416)
   - Tests: tests/utilities/resolve-entity.spec.js (13 tests)

5. **rdf-utils.js** - RDF and Linked Data utilities
   - `listify()` - Convert values to arrays
   - `getSummary()` - Extract descriptions from LD entities
   - Support for SKOS, Dublin Core, and other vocabularies
   - Migrated from: Angular factories "listify" and "getSummary" (lines 669-674, 2078-2100)
   - Tests: tests/utilities/rdf-utils.spec.js (22 tests)

6. **id-generator.js** - ID generation utilities
   - `makeID()` - Generate random base-36 IDs
   - `generateUUID()` - Generate UUID v4
   - `makePrefixedID()`, `makeTimestampID()` - Specialized ID generators
   - Migrated from: Angular service "makeID" (lines 3485-3493)
   - Tests: tests/utilities/id-generator.spec.js (20 tests)

7. **graph.js** - RDF Graph and Resource management
   - `createGraph()` - Create new graph instances
   - `Graph` class - RDF graph with resource management
   - `Resource` class - RDF resource with property handling
   - Support for JSON-LD merge and export
   - Migrated from: Angular factory "Graph" (lines 778-879)
   - Tests: tests/utilities/graph.spec.js (37 tests)

8. **uri-resolver.js** - URI resolution for JSON-LD contexts
   - `resolveURI()` - Resolve compact IRIs to full URIs
   - `compactURI()` - Compact full URIs using context
   - `isFullURI()` - Check if string is a full URI
   - Supports @vocab, prefix expansion, and term mappings
   - Migrated from: Angular service "resolveURI" (lines 3495-3517)
   - Tests: tests/utilities/uri-resolver.spec.js (25 tests)

9. **kg-links.js** - Knowledge graph links service
   - `createLinksService()` - Create links service for KG exploration
   - `createGraphElements()` - Create empty graph structure
   - Node and edge management for Cytoscape.js graphs
   - Probability filtering and type-based styling
   - Migrated from: Angular factory "links" (lines 1945-2076)
   - Tests: tests/utilities/kg-links.spec.js (20 tests)

10. **resource.js** - RDF Resource factory
   - `createResource()` - Create Resource objects with RDF methods
   - Methods: values(), has(), value(), add(), set(), del(), resource()
   - Nested resource management
   - Migrated from: Angular factory "Resource" (lines 676-750)
   - Tests: tests/utilities/resource.spec.js (24 tests)

#### Components (whyis_vue/components/)

1. **resource-link.vue** - Display links to resources with automatic label fetching
   - Automatically fetches and displays labels for URIs
   - Falls back to local part while loading
   - Props: uri (required), label (optional)
   - Migrated from: Angular directive "resourceLink" (lines 923-941)
   - Tests: tests/components/resource-link.spec.js (11 tests)

2. **resource-action.vue** - Links to resource views/actions
   - Creates links for specific actions (edit, view, delete)
   - Props: uri, action (required), label (optional)
   - Migrated from: Angular directive "resourceAction" (lines 943-956)
   - Tests: tests/components/resource-action.spec.js (12 tests)

3. **search-result.vue** - Search results display
   - Displays search results with loading/error states
   - Props: query (required), results (optional)
   - Migrated from: Angular directive "searchResult" (lines 1303-1333)
   - Tests: tests/components/search-result.spec.js (10 tests)

4. **latest-items.vue** - Recent items display
   - Shows recently updated items with labels
   - Props: limit (optional)
   - Migrated from: Angular directive "latest" (lines 1418-1440)
   - Tests: tests/components/latest-items.spec.js (11 tests)

5. **knowledge-explorer.vue** - Knowledge graph visualization
   - Full Cytoscape.js integration for interactive graphs
   - Search, load relationships, probability filtering
   - Props: elements, style, layout, title, start, startList
   - Migrated from: Angular directive "explore" (lines 2163-2620)
   - Tests: tests/components/knowledge-explorer.spec.js (35 tests)

6. **nanopubs.vue** - Nanopublication display and management
   - Lists nanopubs with create/edit/delete functionality
   - Permission-based editing (owner or admin)
   - Props: resource, disableNanopubing, currentUser
   - Migrated from: Angular directive "nanopubs" (lines 1240-1300)
   - Tests: tests/components/nanopubs.spec.js (16 tests)

7. **new-nanopub.vue** - Nanopub creation/editing form
   - Multi-graph editing (assertion, provenance, pubinfo)
   - Format selection and file upload
   - Props: nanopub, verb, editing
   - Migrated from: Angular directive "newnanopub" (lines 1187-1212)
   - Tests: tests/components/new-nanopub.spec.js (21 tests)

8. **new-instance-form.vue** - New instance creation form
   - Form for creating new instances with nanopub structure
   - Label, description, references, provenance support
   - Props: nodeType, lodPrefix, rootUrl
   - Migrated from: Angular controller "NewInstanceController" (lines 3522-3652)
   - Tests: tests/components/new-instance-form.spec.js (27 tests)

9. **edit-instance-form.vue** - Instance editing form
   - Form for editing existing instances
   - Loads instance data via describe endpoint
   - Props: nodeUri, lodPrefix, rootUrl
   - Migrated from: Angular controller "EditInstanceController" (lines 3668-3804)
   - Tests: tests/components/edit-instance-form.spec.js (29 tests)

#### Directives (whyis_vue/directives/)

1. **when-scrolled.js** - Vue directive for scroll triggers
   - Executes callback when element scrolled to bottom
   - Proper cleanup on unbind
   - Migrated from: Angular directive "whenScrolled" (lines 2625-2639)

2. **file-model.js** - Vue directive for file input handling
   - Reads file content and detects format based on extension
   - Automatic format detection using formats utility
   - Event emission for file-loaded and file-error
   - Migrated from: Angular directive "fileModel" (lines 1214-1238)
   - Tests: tests/directives/file-model.spec.js (3 tests)

#### Components (whyis_vue/components/)

1. **resource-link.vue** - Link to resource with automatic label fetching
   - Props: `uri`, `label` (optional)
   - Automatically fetches labels if not provided
   - Migrated from: Angular directive "resourceLink" (lines 923-941)
   - Tests: tests/components/resource-link.spec.js (11 tests)

2. **resource-action.vue** - Link to resource with specific view/action
   - Props: `uri`, `action`, `label` (optional)
   - Supports custom views and actions
   - Migrated from: Angular directive "resourceAction" (lines 943-956)
   - Tests: tests/components/resource-action.spec.js (12 tests)

3. **search-result.vue** - Search results display
   - Props: `query`, `results` (optional)
   - Fetches and displays search results with error handling
   - Migrated from: Angular directive "searchResult" (lines 1303-1333)
   - Tests: tests/components/search-result.spec.js (10 tests)

4. **latest-items.vue** - Latest/recent items display
   - Props: `limit` (optional)
   - Shows latest updated items with timestamps
   - Migrated from: Angular directive "latest" (lines 1418-1440)
   - Tests: tests/components/latest-items.spec.js (11 tests)

5. **knowledge-explorer.vue** - Knowledge graph exploration and visualization
   - Props: `elements`, `style`, `layout`, `title`, `start`, `startList`
   - Full Cytoscape.js integration for graph rendering
   - Interactive node/edge selection and manipulation
   - Search and entity resolution
   - Probability-based filtering
   - Loading states and details sidebar
   - Migrated from: Angular directive "explore" (lines 2163-2620)
   - Tests: tests/components/knowledge-explorer.spec.js (35 tests)

6. **nanopubs.vue** - Nanopublication display and management
   - Props: `resource`, `disableNanopubing`, `currentUser`
   - Lists nanopublications for a resource
   - Create, edit, and delete nanopublications
   - Permission-based editing (owner or admin)
   - Delete confirmation modal
   - Migrated from: Angular directive "nanopubs" (lines 1240-1300)
   - Tests: tests/components/nanopubs.spec.js (16 tests)

7. **new-nanopub.vue** - New/edit nanopublication form
   - Props: `nanopub`, `verb`, `editing`
   - Multi-graph editing (assertion, provenance, pubinfo)
   - Format selection for RDF input
   - File upload with format detection
   - Graph content textarea
   - Migrated from: Angular directive "newnanopub" (lines 1187-1212)
   - Tests: tests/components/new-nanopub.spec.js (21 tests)

### Already Existing Vue Components

These components were already migrated to Vue in previous work:

1. **search-autocomplete.vue** - Search autocomplete with entity resolution
   - Already exists in whyis_vue/components/
   - Equivalent to Angular directive "searchAutocomplete" (lines 1335-1389)

2. **vega-lite-wrapper.vue** - Vega/Vega-Lite visualization wrapper
   - Already exists in whyis_vue/components/
   - Equivalent to Angular directive "vega" (lines 2950-2968)

3. **kg-card.vue** - Knowledge graph entity card display
   - Already exists in whyis_vue/components/
   - Equivalent to Angular directive "kgCard" (lines 2133-2161)

### Already Existing Vue Utilities

These utilities were already migrated to Vue in previous work:

1. **nanopub.js** - Nanopublication CRUD operations
   - Already exists in whyis_vue/utilities/
   - Equivalent to Angular factory "Nanopub" (lines 994-1185)

2. **vega-chart.js** - Vega chart management utilities
   - Already exists in whyis_vue/utilities/
   - Chart specifications, SPARQL data integration, persistence

### Pending Migrations

#### High Priority Angular Components (COMPLETED)

1. ~~**nanopubs** directive (lines 1240-1300)~~
   - ✅ **COMPLETED** - Migrated to nanopubs.vue component

2. ~~**newnanopub** directive (lines 1187-1212)~~
   - ✅ **COMPLETED** - Migrated to new-nanopub.vue component

3. ~~**NewInstanceController** (lines 3522-3652)~~
   - ✅ **COMPLETED** - Migrated to new-instance-form.vue component

4. ~~**EditInstanceController** (lines 3668-3804)~~
   - ✅ **COMPLETED** - Migrated to edit-instance-form.vue component

#### Medium Priority Angular Components

1. **vegaController** directive (lines 2970-3184)
   - Vega chart controller with interactive controls
   - Status: **Optional/Low Priority** - Complex visualization component for interactive charts
   - Note: Basic Vega visualization already supported via vega-lite-wrapper.vue

2. ~~**instanceFacets** directive (lines 3190-3424)~~
   - Status: **Skipped** - Faceted browser no longer used per user request

3. ~~**instanceFacetService** service (lines 2645-2947)~~
   - Status: **Skipped** - Related to faceted browser, no longer used

4. **loadAttributes** factory (lines 3461-3483)
   - Load attribute information for entities
   - Status: **Optional** - May be needed if instance forms need more metadata

#### Low Priority Angular Components

These are lower priority as they may already have Vue equivalents or are not critical:

1. ~~**fileModel** directive (lines 1214-1238)~~
   - ✅ **COMPLETED** - Migrated to file-model.js directive
2. **globalJsonContext** directive (lines 3654-3666) - JSON-LD context injection
3. **whyisSmartFacet** directive (lines 615-627) - Smart facet widget (part of faceted browser)
4. **whyisTextFacet** directive (lines 629-641) - Text facet widget (part of faceted browser)
5. **RecursionHelper** factory (lines 881-921) - Angular recursion helper (may not be needed in Vue)
6. Various services: topClasses, ontologyService, generateLink, getView, transformSparqlData

## Migration Summary

### Completed Work

**Total Migrated:**
- **10 utilities** with 229 tests
- **9 Vue components** with 172 tests  
- **2 Vue directives** with 3 tests

**Grand Total: 404 new tests, all passing ✓**

### Key Achievements

1. **Complete RDF Infrastructure**: All core RDF utilities (Graph, Resource, URI resolution) migrated
2. **Complete Knowledge Graph Exploration**: Full interactive KG explorer with Cytoscape.js
3. **Complete Nanopub Management**: Full CRUD operations with permissions
4. **Complete Instance Management**: Create and edit forms for instances
5. **No Duplication**: Properly identified and reused existing Vue components

### What's Remaining

Only optional/low-priority items remain:
- vegaController for advanced interactive chart controls (optional)
- Various facet widgets (faceted browser deprecated)
- Some helper utilities that may not be needed in Vue

The core migration is **essentially complete**. All high-priority functionality has been migrated to Vue with comprehensive test coverage.

## Migration Principles

### Code Organization

- **Utilities** go in `whyis_vue/utilities/`
- **Components** go in `whyis_vue/components/`
- **Store/State** goes in `whyis_vue/store/`
- **Tests** mirror the source structure in `tests/`

### Testing Requirements

- All migrated code must have comprehensive unit tests
- Tests should cover:
  - Happy path scenarios
  - Error cases
  - Edge cases
  - Integration with other components

### API Compatibility

- Maintain backward compatibility where possible
- Use similar prop names and events as Angular directives
- Document any breaking changes

## Test Coverage

- **Total Test Suites**: 39
- **Total Tests**: 585
- **All Passing**: Yes ✓

### New Test Files Added in This PR

1. `tests/utilities/url-utils.spec.js` - 23 tests
2. `tests/utilities/label-fetcher.spec.js` - 16 tests
3. `tests/utilities/formats.spec.js` - 29 tests
4. `tests/utilities/resolve-entity.spec.js` - 13 tests
5. `tests/utilities/rdf-utils.spec.js` - 22 tests
6. `tests/utilities/id-generator.spec.js` - 20 tests
7. `tests/utilities/graph.spec.js` - 37 tests
8. `tests/utilities/uri-resolver.spec.js` - 25 tests
9. `tests/utilities/kg-links.spec.js` - 20 tests
10. `tests/utilities/resource.spec.js` - 24 tests
11. `tests/components/resource-link.spec.js` - 11 tests
12. `tests/components/resource-action.spec.js` - 12 tests
13. `tests/components/search-result.spec.js` - 10 tests
14. `tests/components/latest-items.spec.js` - 11 tests
15. `tests/components/knowledge-explorer.spec.js` - 35 tests
16. `tests/components/nanopubs.spec.js` - 16 tests
17. `tests/components/new-nanopub.spec.js` - 21 tests
18. `tests/components/new-instance-form.spec.js` - 27 tests
19. `tests/components/edit-instance-form.spec.js` - 29 tests
20. `tests/directives/file-model.spec.js` - 3 tests

**Total: 404 new tests**

## Build Configuration

### Babel Setup

- Using Babel 7 with bridge for Vue component testing
- Configuration in `babel.config.cjs` and `.babelrc`
- Successfully compiling Vue single-file components in tests

### Dependencies

Key development dependencies added/configured:
- `babel-core@^7.0.0-bridge.0` - Babel 7 bridge for vue-jest
- `@babel/core@^7.28.4` - Babel 7 core
- `@babel/preset-env@^7.28.3` - Babel preset
- `vue-jest@^3.0.7` - Vue component testing

## Usage Examples

### Using URL Utilities

```javascript
import { getParameterByName, decodeDataURI } from '@/utilities/url-utils';

// Get query parameter
const query = getParameterByName('q'); // from ?q=search

// Decode data URI
const result = decodeDataURI('data:text/plain;base64,SGVsbG8=');
console.log(result.value); // 'Hello'
```

### Using Label Fetcher

```javascript
import { getLabel, getLabelSync } from '@/utilities/label-fetcher';

// Async label fetch
const label = await getLabel('http://example.org/resource/123');

// Sync from cache
const cachedLabel = getLabelSync('http://example.org/resource/123');
```

### Using Format Utilities

```javascript
import { getFormatFromFilename, isFormatSupported } from '@/utilities/formats';

// Get format from filename
const format = getFormatFromFilename('data.ttl');
console.log(format.mimetype); // 'text/turtle'

// Check if format is supported
if (isFormatSupported('rdf')) {
  // Handle RDF file
}
```

### Using Vue Components

```vue
<template>
  <div>
    <!-- Resource link with automatic label fetching -->
    <resource-link :uri="resourceUri" />
    
    <!-- Resource link with custom label -->
    <resource-link :uri="resourceUri" label="Custom Label" />
    
    <!-- Resource action link -->
    <resource-action :uri="resourceUri" action="edit" />
  </div>
</template>

<script>
import ResourceLink from '@/components/resource-link.vue';
import ResourceAction from '@/components/resource-action.vue';

export default {
  components: {
    ResourceLink,
    ResourceAction
  },
  data() {
    return {
      resourceUri: 'http://example.org/resource/123'
    };
  }
};
</script>
```

## Template Migrations

### Completed Vue-based Templates (base_vue.html)

1. **edit_instance_view_vue.html** - Edit instance form using Vue
   - Uses `edit-instance-form.vue` component
   - Bootstrap 5 styling
   - Replaces Angular-based `edit_instance_view.html`

2. **new_instance_view_vue.html** - New instance creation form using Vue
   - Uses `new-instance-form.vue` component
   - Bootstrap 5 styling
   - Replaces Angular-based `new_instance_view.html`

3. **explore_vue.html** - Knowledge graph exploration using Vue
   - Uses `knowledge-explorer.vue` component
   - Full-screen layout for graph visualization
   - Replaces Angular-based `explore.html`

4. **concept_view_vue.html** - Concept/class view using Vue
   - Uses `nanopubs.vue` for commentary
   - Bootstrap 5 card-based layout
   - Replaces Angular-based `concept_view.html`

### Using Vue Templates

These templates extend `base_vue.html` which provides:
- Bootstrap 5 framework
- Vue.js integration
- Modern responsive navigation
- Search autocomplete component
- Upload knowledge modal

To use Vue templates in routes, update view handlers to render the `_vue` versions.

## Migration Complete

✅ **All high-priority components migrated**
✅ **585 tests passing (404 new)**
✅ **Key templates migrated to Vue**
✅ **Comprehensive documentation**

### Remaining Optional Items

- vegaController for advanced chart interactions (basic Vega supported)
- Additional template conversions (can be done incrementally)
- Removal of legacy Angular code (after full validation)

## Notes

- Vue and Angular templates coexist - choose which to use per route
- Both systems fully functional
- Migration provides modern, maintainable codebase
- Comprehensive test coverage ensures reliability
