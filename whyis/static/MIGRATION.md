# Angular to Vue.js Migration Guide

## Overview

This document tracks the migration of Angular.js code from `whyis/static/js/whyis.js` to Vue.js components in the `whyis/static/js/whyis_vue/` directory.

## Migration Status

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

#### Directives (whyis_vue/directives/)

1. **when-scrolled.js** - Vue directive for scroll triggers
   - Executes callback when element scrolled to bottom
   - Proper cleanup on unbind
   - Migrated from: Angular directive "whenScrolled" (lines 2625-2639)

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

### Already Existing Vue Components

These components were already migrated to Vue in previous work:

1. **search-autocomplete.vue** - Search autocomplete with entity resolution
   - Already exists in whyis_vue/components/
   - Equivalent to Angular directive "searchAutocomplete" (lines 1335-1389)

### Pending Migrations

#### High Priority Angular Directives

1. **nanopubs** (lines 1240-1300)
   - Nanopublication display and management
   - Complex component with nested directives
   - Status: **Pending**

2. **newnanopub** (lines 1187-1212)
   - New nanopublication creation form
   - Requires nanopub utilities
   - Status: **Pending**

3. ~~**searchResult** (lines 1303-1333)~~
   - ✅ **COMPLETED** - Migrated to search-result.vue

4. ~~**latest** (lines 1418-1440)~~
   - ✅ **COMPLETED** - Migrated to latest-items.vue

5. **vega** (lines 2950-2968)
   - Vega visualization wrapper
   - May already have Vue equivalent

6. **vegaController** (lines 2970-3184)
   - Vega chart controller
   - Complex visualization logic

#### Angular Services to Migrate

1. ~~**resolveEntity** (lines 1391-1416)~~
   - ✅ **COMPLETED** - Migrated to resolve-entity.js utility

2. **Nanopub** factory (lines 994-1185)
   - Nanopublication CRUD operations
   - Complex service with many methods
   - Status: **Pending**

3. **Graph** factory (lines 778-879)
   - ✅ **COMPLETED** - Migrated to graph.js utility

4. **Resource** factory (lines 676-750)
   - Resource object handling
   - Used throughout the codebase

#### Angular Controllers to Consider

1. **NewInstanceController** (lines 3522-3649)
   - New instance creation
   - Complex form handling

2. **EditInstanceController** (lines 3668-3804)
   - Instance editing
   - Similar to NewInstanceController

3. **SmartFacetController** (lines 556-562)
   - Faceted search controller
   - May be part of existing facet system

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

- **Total Test Suites**: 24
- **Total Tests**: 275
- **All Passing**: Yes ✓

### New Test Files

1. `tests/utilities/url-utils.spec.js` - 23 tests
2. `tests/utilities/label-fetcher.spec.js` - 16 tests
3. `tests/utilities/formats.spec.js` - 29 tests
4. `tests/components/resource-link.spec.js` - 11 tests
5. `tests/components/resource-action.spec.js` - 12 tests

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

## Next Steps

1. **Priority 1**: Migrate core RDF utilities (Graph, Resource factories)
2. **Priority 2**: Migrate Nanopub service and components
3. **Priority 3**: Migrate search and display components
4. **Priority 4**: Migrate complex controllers (NewInstance, EditInstance)
5. **Priority 5**: Update templates to use Vue components

## Notes

- The existing Angular app remains functional during migration
- Vue components are being introduced gradually
- Both systems can coexist temporarily
- Full migration will require template updates
