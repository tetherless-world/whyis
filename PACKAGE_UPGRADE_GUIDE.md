# Package Upgrade Migration Guide

## Overview

This guide documents the major package upgrades in Whyis and provides migration instructions for developers and users.

## Major Package Upgrades

### Flask Ecosystem (Flask 1.x → 3.x)

The Flask ecosystem has been upgraded to version 3.x with all compatible dependencies:

- **Flask**: 1.x → 3.0+
  - Flask 3.x is backwards compatible with most Flask 1.x code
  - Removed deprecated APIs (like `flask._compat`, `_request_ctx_stack`)
  
- **Jinja2**: 2.11.3 → 3.1+
  - Mostly backwards compatible
  - Some template syntax edge cases may behave differently
  
- **Werkzeug**: 2.0.3 → 3.0+
  - API is mostly compatible
  - `__version__` not exposed at top level in 3.x (not an issue for normal usage)
  
- **itsdangerous**: <2.0 → 2.2+
  - API compatible with 2.x
  
- **markupsafe**: 2.0.1 → 3.0+
  - Compatible with Jinja2 3.x

### Flask Extensions

- **Flask-Security → Flask-Security-Too**: 3.0.0 → 5.3+
  - Drop-in replacement, import name stays `flask_security`
  - No code changes required
  - Note: `encrypt_password()` is now `hash_password()` (but old name still works)

- **Flask-Login**: 0.5.0 → 0.6+
- **Flask-WTF**: <0.15 → 1.2+
- **Flask-Caching**: 1.10.1 → 2.3+
- **Flask-Script**: 2.0.6 (kept for backwards compatibility with patches)
  - Deprecated, but patched for Flask 3.x compatibility
  - New Click-based CLI available via `whyis-cli` command

### RDF and Semantic Web

- **rdflib**: 6.3.2 → 7.0+
  - Major version upgrade
  - API is backwards compatible for most use cases
  - Some plugin changes (should not affect normal usage)
  - All Whyis code works with rdflib 7.x

- **oxrdflib**: 0.3.1 → 0.5.0
- **sadi**: (unversioned) → 1.0.0
- **setlr**: >=1.0.1 (kept constraint)
- **sdd2rdf**: >=1.3.2 → >=1.6.0

### Data Processing

- **beautifulsoup4**: 4.7.1 → 4.12+
  - Backwards compatible
  
- **numpy**: (unversioned) → 1.22.0-1.24.x (constrained for Python 3.8 compatibility)
  - NumPy 2.0+ requires Python 3.9+
  - Python 3.8 users will get NumPy 1.24.x (last version supporting 3.8)
  
- **pandas**: (unversioned) → 1.5.x (constrained for Python 3.8 compatibility)
  - Pandas 2.0+ requires Python 3.9+
  - Python 3.8 users will get Pandas 1.5.x (last version supporting 3.8)
  
- **scipy**: (unversioned) → 1.10.x (constrained for Python 3.8 compatibility)
  - SciPy 1.11+ requires Python 3.9+
  - Python 3.8 users will get SciPy 1.10.x (last version supporting 3.8)
  
- **lxml**: (unversioned) → latest
- **nltk**: 3.6.5 → 3.9+

### Other Utilities

- **celery**: <6.0.0 → >=5.4.0,<6.0.0
- **eventlet**: >=0.35.2 → >=0.40.0
- **dnspython**: 2.2.1 → 2.8+
- **email_validator**: 1.1.3 → 2.3+
- **cookiecutter**: 1.7.3 → 2.6+
- **bibtexparser**: 1.1.0 → 1.4+
- **filedepot**: 0.10.0 → 0.11.0
- **ijson**: 2.4 → 3.3+
- **puremagic**: 1.14 → 1.28+

## Flask-Script to Flask CLI Migration

### Background

Flask-Script is deprecated and incompatible with Flask 3.x. We've taken a two-pronged approach:

1. **Backwards compatibility**: Added compatibility patches to make Flask-Script work with Flask 3.x
2. **Modern CLI**: Created new Click-based CLI for future use

### Using the Old `whyis` Command (Flask-Script)

The existing `whyis` command continues to work with Flask 3.x thanks to compatibility patches:

```bash
whyis run
whyis createuser -u admin -p password
whyis load data.ttl
```

These patches inject missing Flask APIs:
- `flask._compat` module
- `flask._request_ctx_stack` 
- `flask._app_ctx_stack`

### Using the New `whyis-cli` Command (Click-based)

A new modern CLI is available using Flask's built-in Click support:

```bash
whyis-cli run
whyis-cli createuser -u admin -p password
whyis-cli load data.ttl
```

**Available commands:**
- `run` - Run development server with embedded services
- `createuser` - Create a new user
- `updateuser` - Update an existing user
- `load` - Load a nanopublication from file
- `retire` - Retire a nanopublication
- `backup` - Backup the application
- `restore` - Restore from backup
- `init` - Initialize the application
- `sanitize` - Sanitize the knowledge graph
- `test` - Run tests
- `runagent` - Run a specific agent

### Subprocess Management

Both CLIs preserve the important subprocess management:
- **CleanChildProcesses**: Process group management for clean shutdown
- **Embedded Celery**: Automatic Celery worker spawning
- **Embedded Fuseki**: Fuseki server management
- **Webpack watching**: Frontend build process management

## Python Version Support

- **Minimum Python version**: 3.8 (changed from 3.7)
- **Tested versions**: 3.8, 3.9, 3.10, 3.11 (per CI configuration)
- Python 3.12 should also work but is not officially tested in CI

## Breaking Changes

### None for Normal Usage

For typical Whyis usage, there should be no breaking changes. All tests pass with the upgraded packages.

### Potential Edge Cases

1. **Flask-Script deprecation**: If you've extended Flask-Script commands, you may want to migrate to Click-based commands

2. **Direct use of deprecated Flask APIs**: If your custom code uses:
   - `flask._compat`
   - `flask._request_ctx_stack`
   - `flask._app_ctx_stack`
   
   You'll need to either update your code or ensure the compatibility patches are loaded.

3. **rdflib plugin changes**: If you've written custom rdflib plugins, test with rdflib 7.x

4. **Template edge cases**: Some Jinja2 3.x template behaviors may differ slightly from 2.x

## Python Version Support

- **Minimum Python version**: 3.8 (changed from 3.7)
- **Tested versions**: 3.8, 3.9, 3.10, 3.11 (per CI configuration)
- Python 3.12 should also work but is not officially tested in CI

### Python 3.8 Specific Notes

Some packages have dropped Python 3.8 support in their latest versions. The dependency specifications include upper bounds to ensure Python 3.8 compatibility:

- **NumPy**: Constrained to `<2.0.0` (NumPy 2.0+ requires Python 3.9+)
  - Python 3.8 will install NumPy 1.24.x (last series supporting 3.8)
  
- **Pandas**: Constrained to `<2.0.0` (Pandas 2.0+ requires Python 3.9+)
  - Python 3.8 will install Pandas 1.5.x (last series supporting 3.8)
  
- **SciPy**: Constrained to `<1.11.0` (SciPy 1.11+ requires Python 3.9+)
  - Python 3.8 will install SciPy 1.10.x (last series supporting 3.8)

These constraints ensure the package can be installed on Python 3.8 (as used in Docker builds) while allowing newer versions on Python 3.9+.

## Testing Your Application

After upgrading, run your test suite:

```bash
# Run unit tests
pytest tests/unit/

# Run all tests
pytest

# Run with coverage
pytest --cov=whyis --cov-report=html
```

## Migration Checklist

- [ ] Update `requirements.txt` or `setup.py` to use new package versions
- [ ] Run your test suite to ensure no regressions
- [ ] Test critical user workflows
- [ ] Update any custom Flask-Script commands to Click (optional, Flask-Script still works)
- [ ] Test embedded services (Celery, Fuseki) work correctly
- [ ] Check that all autonomous agents function properly
- [ ] Verify nanopublication loading and management
- [ ] Test user authentication and authorization

## Getting Help

If you encounter issues:

1. Check if Flask-Script compatibility patches are loaded (for `whyis` command)
2. Try the new `whyis-cli` command as an alternative
3. Review Flask 3.x migration guide: https://flask.palletsprojects.com/en/3.0.x/changes/
4. Check rdflib 7.x release notes: https://github.com/RDFLib/rdflib/releases
5. Open an issue on GitHub with details about your problem

## Benefits of These Upgrades

- **Security**: Latest versions include security fixes
- **Performance**: Newer packages often have performance improvements
- **Python 3.12 support**: Ready for newer Python versions
- **Active maintenance**: All upgraded packages are actively maintained
- **Modern tooling**: Click-based CLI is more maintainable and feature-rich
- **Dependency compatibility**: Better compatibility with modern Python ecosystem
