# GitHub Copilot Instructions for Whyis

This document provides guidance for GitHub Copilot when working on the Whyis project.

## Project Overview

Whyis is a nano-scale knowledge graph publishing, management, and analysis framework built with Python and Flask. It manages knowledge as nanopublications, which are the smallest publishable units of knowledge graphs with associated provenance and publication information.

### Key Technologies

- **Backend**: Python 3.8+ with Flask web framework (CI tests 3.8-3.11)
- **Knowledge Graph**: RDF, OWL, SPARQL, rdflib
- **Database**: Apache Jena Fuseki (included in setup)
- **Frontend**: Vue.js components, JavaScript
- **Task Queue**: Celery with Redis backend
- **Testing**: pytest, pytest-flask, pytest-cov
- **Linting**: pylint

## Repository Structure

```
whyis/
├── whyis/                  # Main Python package
│   ├── autonomic/         # Autonomous agents (FRIR, SETLR, etc.)
│   ├── blueprint/         # Flask blueprints
│   ├── commands/          # CLI commands
│   ├── config/            # Configuration modules
│   ├── database/          # Database utilities
│   ├── datastore/         # Data storage
│   ├── fuseki/            # Fuseki server integration
│   ├── importer/          # Data importers
│   ├── nanopub/           # Nanopublication handling
│   ├── plugins/           # Plugin system
│   ├── static/            # Frontend assets (JS, CSS, Vue components)
│   └── templates/         # Jinja2 templates
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── api/              # API endpoint tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
└── examples/              # Example applications
```

## Development Workflow

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-test.txt

# Install package in editable mode
pip install -e .

# Build frontend assets
cd whyis/static
npm install
npm run build-dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=whyis --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_namespace.py

# Run tests in verbose mode
pytest -v

# Run tests and stop at first failure
pytest -x
```

### Code Quality

```bash
# Run pylint
pylint whyis/

# Check specific module
pylint whyis/namespace.py
```

## Coding Conventions

### Python Style

- **Follow PEP 8** for Python code style
- **Python 3.8+ syntax**: Use type hints where appropriate
- **Docstrings**: Use clear docstrings for modules, classes, and functions
- **Imports**: Group imports (standard library, third-party, local) with blank lines between groups
- **Line length**: Keep lines under 100 characters when possible

### Testing Conventions

- **Test files**: Use `test_*.py` naming convention
- **Test classes**: Start with `Test` prefix (e.g., `TestNamespace`)
- **Test functions**: Start with `test_` prefix
- **Arrange-Act-Assert pattern**: Structure tests clearly:
  ```python
  def test_function():
      # Arrange - set up test data
      input_data = prepare_data()
      
      # Act - execute the function being tested
      result = function_to_test(input_data)
      
      # Assert - verify the results
      assert result == expected_value
  ```
- **Use fixtures**: Define reusable test fixtures in `conftest.py`
- **Test coverage goal**: Aim for >80% coverage on new code
- **Docstrings in tests**: Explain what is being tested

### RDF and Semantic Web Conventions

- **Use rdflib**: For RDF graph operations
- **Namespaces**: Define namespaces in `whyis.namespace` module
- **SPARQL queries**: Use parameterized queries to prevent injection
- **URIs**: Follow best practices for URI design

### Flask Conventions

- **Blueprints**: Organize routes using Flask blueprints (but prefer view infrastructure over new routes)
- **Templates**: Use Jinja2 templates in `whyis/templates/` with the view infrastructure
- **Static files**: Place in `whyis/static/`
- **Configuration**: Use Flask configuration system
- **Views**: Prefer `current_app.render_view(resource)` over custom route handlers
- **Plugins**: Use Flask-PluginEngine for modular functionality

## Common Patterns

### Using the View Infrastructure

The preferred way to display resources is through the existing view infrastructure:

```python
from flask import current_app

# Get a resource by URI
resource = current_app.get_resource(entity_uri)

# Render the resource using the view system
# This automatically selects the appropriate template based on resource type
return current_app.render_view(resource)

# Render with a specific view
return current_app.render_view(resource, view='describe')
```

Resources are accessed via URI paths that get resolved by the view infrastructure. For example:
- `/about` - resolves to the "about" resource URI
- `/home` - resolves to the "home" resource URI  
- `/<path:name>` - resolves to any resource by its path

The view infrastructure automatically:
- Resolves the entity URI from the path
- Loads the resource and its properties from the knowledge graph
- Selects the appropriate template based on resource type
- Renders the view with all resource data

#### Registering Views in Vocabulary Files

**IMPORTANT**: The `render_view()` system is driven by the vocabulary system. New views must be registered in vocabulary files to be used.

Views are defined in:
- `whyis/default_vocab.ttl` - System-level view definitions
- Application `vocab.ttl` - Application-specific view definitions

**To register a new view for a resource type:**

```turtle
# In vocab.ttl file
@prefix whyis: <http://vocab.rpi.edu/whyis/> .

# Register a view template for a class
my:CustomClass a owl:Class;
  whyis:hasView "custom_view.html";
  whyis:editInstanceView "custom_edit.html".

# Or define a custom view property
whyis:hasCustomView rdfs:subPropertyOf whyis:hasView;
  dc:identifier "custom".

# Then associate it with a class
rdfs:Resource whyis:hasCustomView "custom_template.html".
```

Common view properties:
- `whyis:hasView` - Default view template
- `whyis:editInstanceView` - Edit form template
- `whyis:hasGraphView` - RDF graph view
- `whyis:hasDescribe` - JSON-LD describe view
- Custom properties that extend `whyis:hasView`

Without vocabulary registration, `render_view()` won't know which template to use for a resource type.

### Working with Nanopublications

```python
from whyis.nanopub import Nanopublication

# Create a nanopublication
nanopub = Nanopublication()
nanopub.assertion.add((subject, predicate, object))
nanopub.provenance.add((assertion_uri, prov.wasAttributedTo, agent))
```

### Using Autonomous Agents

Autonomous agents process data automatically. They are located in `whyis/autonomic/`.

- Inherit from base agent classes
- Implement required methods (`process`, `getInputClass`, etc.)
- Register agents in application configuration

### Database Operations

```python
from whyis.database import database

# Query using SPARQL
results = database.query("""
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    LIMIT 10
""")
```

### Working with Vocabulary Files

Vocabulary files (`.ttl` format) define:
- Resource type definitions and hierarchies
- View template associations for resource types
- Property definitions and constraints
- Application ontology

**Key vocabulary files:**
- `whyis/default_vocab.ttl` - System vocabulary (typically don't modify)
- Application `vocab.ttl` - Application-specific vocabulary

**Common vocabulary patterns:**

```turtle
# Define a new class with views
my:CustomClass a owl:Class;
  rdfs:label "Custom Resource Type";
  whyis:hasView "custom_view.html";
  whyis:editInstanceView "custom_edit.html".

# Define properties
my:customProperty a owl:DatatypeProperty;
  rdfs:label "Custom Property";
  rdfs:domain my:CustomClass;
  rdfs:range xsd:string.

# Register navigation items
my:CustomClass whyis:hasNavigation (
  whyis:hasView
  whyis:hasGraphView
  whyis:editInstanceView
).
```

When adding templates, remember to register them in the vocabulary file so `render_view()` can find them.

## Testing Guidelines

### Unit Tests

- Test individual functions and methods in isolation
- Mock external dependencies (database, file system, network)
- Keep tests fast and focused
- Located in `tests/unit/`

### Integration Tests

- Test interactions between components
- May require application context
- Located in `tests/integration/`

### API Tests

- Test Flask routes and endpoints
- Use Flask test client
- Located in `tests/api/`

### Test Fixtures

Common fixtures available from `tests/conftest.py`:
- `app`: Flask application instance
- `client`: Test client for making requests
- `runner`: CLI runner for testing commands

## Dependencies

### Adding New Dependencies

When adding a new Python dependency:

1. Add to `install_requires` in `setup.py` with appropriate version constraints
2. Use version constraints that match the project's pattern:
   - Exact pins (==) for known stable versions
   - Upper bounds (<) to prevent breaking changes
   - Lower bounds (>=) when requiring specific features
3. Test compatibility with Python 3.8-3.11 (versions tested in CI)
4. Document why the dependency is needed (especially with version constraints)

### Frontend Dependencies

JavaScript dependencies are managed with npm:
- Add to `whyis/static/package.json`
- Run `npm install` to update
- Commit `package-lock.json` changes

## Security Considerations

- **Input validation**: Always validate and sanitize user input
- **SPARQL injection**: Use parameterized queries
- **XSS prevention**: Escape HTML output in templates
- **Authentication**: Use Flask-Security for user authentication
- **Authorization**: Check permissions before sensitive operations
- **Dependencies**: Keep dependencies up to date for security patches

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Python Tests**: Run on push/PR for Python code changes
- **Vue.js Tests**: Run for frontend changes
- **Frontend CI**: Build and lint frontend assets
- **Multiple Python versions**: Tests run on Python 3.8-3.11

Configuration files:
- `.github/workflows/python-tests.yml`
- `.github/workflows/vue-tests.yml`
- `.github/workflows/frontend-ci.yml`

## Build Process

### Python Package

```bash
# Build package
python setup.py build

# Create distribution
python setup.py sdist
```

The build process:
1. Builds JavaScript assets with npm
2. Downloads Fuseki JAR files
3. Packages Python code

### Frontend Assets

```bash
cd whyis/static
npm run build-dev      # Development build
npm run build          # Production build
```

## Common Tasks

### Adding a New Module

1. Create the module in appropriate `whyis/` subdirectory
2. Write comprehensive unit tests in `tests/unit/`
3. Add docstrings to all public functions/classes
4. Import and expose in `__init__.py` if needed
5. Update documentation if it's a public API

### Adding Features (Routes and Views)

**IMPORTANT**: Avoid adding new routes whenever possible. The existing view infrastructure should be used instead.

**For read operations:**
1. Use the existing view infrastructure with templates in `whyis/templates/`
2. Resources are automatically rendered using `current_app.render_view(resource)`
3. Views can be customized per resource type using the template system
4. Access resources via their URI paths (handled by existing entity routes)
5. **Register new views in vocabulary files** (`default_vocab.ttl` or app `vocab.ttl`)

**For write operations:**
1. Post nanopublications to the `/pub` route (see nanopublication blueprint)
2. Avoid creating new write endpoints
3. Represent data changes as nanopublications in the knowledge graph

**Only if a new route is absolutely necessary:**

New routes should only be added in rare cases, such as:
- Custom API endpoints that cannot be represented as resource views
- Integration endpoints for external services
- Administrative or system-level operations not tied to specific resources

If adding a route:
1. Document justification for why existing infrastructure cannot be used
2. Add route to appropriate blueprint in `whyis/blueprint/`
3. Implement route handler function
4. Add template if needed in `whyis/templates/`
5. Write API tests in `tests/api/`
6. Update documentation

### Adding a New Autonomous Agent

1. Create agent class in `whyis/autonomic/`
2. Inherit from appropriate base class
3. Implement required methods
4. Write unit tests in `tests/unit/whyis_test/autonomic/`
5. Register agent in configuration
6. Document agent purpose and configuration

### Creating a Plugin for Modularity

**IMPORTANT**: Encapsulate logically related functionality in plugins to maximize application modularity.

Plugins provide:
- Self-contained functionality with their own blueprints, templates, and static files
- Event listeners (NanopublicationListener, EntityResolverListener)
- Custom filters and template functions
- Optional vocabulary (vocab.ttl) to extend the knowledge graph

**To create a plugin:**

1. Create plugin directory in `whyis/plugins/<plugin_name>/`
2. Implement plugin class inheriting from `whyis.plugin.Plugin`
3. Define plugin structure:
   ```python
   from whyis.plugin import Plugin, PluginBlueprint
   
   class MyPlugin(Plugin):
       def create_blueprint(self):
           # Optional: create blueprint for routes
           blueprint = PluginBlueprint('my_plugin', __name__)
           # Add routes to blueprint
           return blueprint
       
       def vocab(self, store):
           # Optional: load plugin vocabulary
           super().vocab(store)
   ```
4. Optionally add listener classes (NanopublicationListener, EntityResolverListener)
5. Register plugin in `setup.py` entry_points under 'whyis'
6. Add plugin templates in plugin directory
7. Write tests for plugin functionality
8. Document plugin purpose and configuration

**Use plugins for:**
- Domain-specific functionality
- Integrations with external services
- Custom entity resolvers
- Specialized views or data transformations
- Event-driven processing of nanopublications

## Documentation

- **README.md**: Project overview and quick start
- **TESTING.md**: Detailed testing documentation
- **docs/**: Full documentation (ReadTheDocs)
- **Docstrings**: Inline code documentation

When making changes:
- Update relevant documentation
- Keep README.md examples current
- Update TESTING.md if test patterns change

## Getting Help

- **Documentation**: http://whyis.readthedocs.io
- **Issues**: GitHub issue tracker
- **Testing docs**: See TESTING.md in repository

## Tips for Copilot

- **Architecture first**: Before adding routes, consider using the view infrastructure or plugins
- **Avoid new routes**: Use `render_view()` for reads, `/pub` route for writes via nanopublications
- **Plugin modularity**: Encapsulate logically related functionality in plugins
- **Minimal changes**: Make the smallest possible changes to fix issues
- **Test-driven**: Write tests first when adding features
- **Follow patterns**: Look at existing code for patterns and conventions
- **Coverage**: Maintain or improve test coverage
- **Documentation**: Update docs when changing APIs
- **Dependencies**: Avoid adding unnecessary dependencies
- **Python version**: Ensure compatibility with Python 3.8-3.11 (versions tested in CI)
- **Type hints**: Add type hints to new functions
- **Error handling**: Add appropriate error handling and logging
- **RDF best practices**: Follow semantic web standards and conventions
