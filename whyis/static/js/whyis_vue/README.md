# Whyis Vue.js Application

This directory contains the Vue.js frontend application for Whyis, a knowledge graph platform for scientific research and data visualization.

## Overview

The Whyis Vue application provides an interactive interface for managing and visualizing knowledge graphs, with specialized support for scientific datasets, SPARQL queries, and Vega-Lite visualizations.

## Architecture

### Directory Structure

```
whyis_vue/
├── assets/                 # CSS/SCSS stylesheets and static assets
├── components/             # Vue.js components (52 files)
│   ├── gallery/           # Chart gallery components
│   ├── pages/             # Page-level components
│   │   ├── dataset/       # Dataset management pages
│   │   ├── sparql-templates/ # SPARQL template editor
│   │   └── vega/          # Visualization editor pages
│   ├── table-view/        # Table visualization components
│   └── utils/             # Utility components (dialogs, spinners, etc.)
├── mixins/                # Reusable Vue component logic
├── modules/               # Shared functionality modules
│   └── events/            # Event handling services
├── store/                 # Vuex state management
├── utilities/             # Core utility functions
└── main.js               # Application entry point
```

### Key Technologies

- **Vue.js 2.6** - Progressive JavaScript framework
- **Vuex** - State management with persistence
- **Vue Material** - Material Design components
- **Vega-Lite** - Data visualization grammar
- **Axios** - HTTP client for API requests
- **SPARQL** - Query language for RDF data

## Core Modules

### Utilities (`utilities/`)
Provides fundamental functionality for the application:

- **`vega-chart.js`** - Chart creation, loading, and SPARQL integration
- **`nanopub.js`** - Nanopublication CRUD operations
- **`sparql.js`** - SPARQL query execution
- **`dataset-upload.js`** - Dataset management and upload
- **`orcid-lookup.js`** - ORCID researcher ID validation
- **`views.js`** - Navigation and view management
- **`debounce.js`** - Function execution delay utility
- **`common-namespaces.js`** - RDF namespace constants
- **`autocomplete-menu.js`** - UI autocomplete functionality
- **`dialog-box-adjust.js`** - Dialog positioning utilities

### Store (`store/`)
Vuex-based state management:

- **`index.js`** - Main store configuration with persistence
- **`viz-editor.js`** - Chart editor state management

### Components (`components/`)
Vue.js components organized by functionality:

- **Pages** - Full-page components for different application views
- **Gallery** - Chart gallery and visualization browsing
- **Utils** - Reusable utility components (spinners, dialogs, headers)
- **Table View** - Tabular data display components

### Modules (`modules/`)
Shared application services:

- **Event Services** - Central event bus for component communication
- **Slugs** - String conversion utilities for URL-safe identifiers

### Mixins (`mixins/`)
Reusable component functionality:

- **View Mixin** - Common view-related properties and methods

## Key Features

### 1. Interactive Data Visualization
- Vega-Lite integration for rich, interactive charts
- SPARQL query results visualization
- Chart gallery with filtering and search
- Real-time chart editing and preview

### 2. Knowledge Graph Management
- Nanopublication-based data storage
- RDF/Linked Data support
- SPARQL query interface
- Semantic data relationships

### 3. Dataset Management
- File upload and metadata management
- DOI integration for research publications
- ORCID author identification
- Rich metadata editing with validation

### 4. User Interface
- Material Design components
- Responsive layout
- Progressive loading
- Real-time state synchronization

## Getting Started

### Prerequisites
- Node.js (version specified in package.json)
- npm or yarn package manager

### Installation
```bash
cd whyis/static
npm install
```

### Development
```bash
npm run start    # Development build with watch mode
npm run build    # Production build
npm run lint     # Code linting (requires ESLint setup)
```

### Build Output
The build process generates optimized bundles in the `dist/` directory:
- `main.js` - Core application bundle
- `vega-lite-wrapper.js` - Visualization components
- `data-voyager.js` - Data exploration interface
- Component-specific chunks for code splitting

## API Integration

The application integrates with Whyis backend APIs:

- **SPARQL Endpoint** - `/sparql` for RDF queries
- **Nanopublication API** - `/pub` for data storage
- **Entity Resolution** - `/?term=*&view=resolve` for autocomplete
- **ORCID Integration** - `/orcid/` for researcher identification
- **DOI Resolution** - `/doi/` for publication metadata

## State Management

The application uses Vuex for centralized state management:

- **Persistent State** - User preferences and session data
- **Chart Editor** - Visualization creation and editing state
- **Event Bus** - Component communication via the EventServices module

## Configuration

Global configuration is provided via server-rendered variables:
- `ROOT_URL` - Application base URL
- `LOD_PREFIX` - Linked Open Data URI prefix
- `USER` - Current user information
- `NODE_URI` - Current entity URI
- `NAVIGATION` - Site navigation structure

## Contributing

When contributing to the Vue.js application:

1. Follow existing code patterns and documentation standards
2. Use JSDoc comments for all functions and modules
3. Test changes with `npm run build` before committing
4. Ensure components are properly documented with props, data, and methods
5. Use semantic commit messages

## Module Documentation

All modules in this directory are documented using JSDoc format. Key documentation includes:

- Module descriptions and purposes
- Function parameter types and return values
- Usage examples where appropriate
- Vue component props, data, computed properties, and methods

For detailed API documentation of individual modules, refer to the JSDoc comments in each file.