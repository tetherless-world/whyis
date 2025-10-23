# Whyis

[![Python Tests](https://github.com/tetherless-world/whyis/workflows/Python%20Tests/badge.svg)](https://github.com/tetherless-world/whyis/actions/workflows/python-tests.yml)
[![Vue.js Tests](https://github.com/tetherless-world/whyis/workflows/Vue.js%20Tests/badge.svg)](https://github.com/tetherless-world/whyis/actions/workflows/vue-tests.yml)
[![Frontend CI](https://github.com/tetherless-world/whyis/workflows/Frontend%20CI/badge.svg)](https://github.com/tetherless-world/whyis/actions/workflows/frontend-ci.yml)

[Visit our project web site for more details on how to use Whyis.](http://whyis.readthedocs.io)

Whyis is a nano-scale knowledge graph publishing, management, and analysis framework.
Whyis aims to support domain-aware management and curation of knowledge from many different sources. Its primary goal is to enable creation of useful domain- and data-driven knowledge graphs. Knowledge can be contributed and managed through direct user interaction, statistical analysis, or data ingestion from many different kinds of data sources. Every contribution to the knowledge graph is managed as a separate entity so that its provenance (publication status, attribution, and justification) is transparent and can be managed and used.

Whyis manages its fragments of knowledge as nanopublications, which can be viewed as the smallest publishable unit. They are fragments of knowledge graphs that have secondary graphs associated with them to contain provenance and publication information. Knowledge graph systems need to manage the provenance of its contents. By using existing recommended standards like RDF, OWL, and SPARQL, nanopublications are able to provide flexible expansion and integration options without the limitations of custom database management tools. They also have the flexibility to capture any level of granularity of information required by the application.

Every entity in the resource is visible through its own Uniform Resource Identifier (URI), and is available as machine-readable linked data. When a user accesses the URI, all the nanopublications about it are aggregated together into a single graph. This approach gives users the ability to control access to this knowledge. It also provides the ability to control the publishing workflow. Rather than publishing everything immediately, nanopublications can be contributed, curated and approved, and then finally published either individually or in collections. Knowledge graph developers can flexibly control the ways in which the entities are shown to users by their type or other constraints. We provide default views for knowledge graph authoring, including for ontology development and also allow developers to provide customized views. Our plan is to base our new enhanced Nanomine on the Whyis infrastructure to enable more flexibility and extensibility.

# Nano-scale?

Nano-scale knowledge graphs are built of many *[nanopublications](http://nanopub.org)*, where each nanopublication is tracked individually, with the ability to provide provenance-based justifications and publication credit for each tiny bit of knowledge in the graph.

## Testing

Whyis uses pytest for its Python testing framework. To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=whyis --cov-report=html
```

For detailed testing documentation, see [TESTING.md](TESTING.md).

Current test coverage:
- **136 unit tests** covering 7 core utility modules (namespace, data_formats, data_extensions, html_mime_types, version, parse_data_url, datastore_utils)
- **26 component tests** for autonomic agents (CacheUpdater, Crawler, DatasetImporter, Deductor)
- API tests for nanopublication CRUD operations
- Integration tests for autonomous agents (FRIR, OntologyImporter, SETLR)
- Vue.js component tests (149 tests)

Tests run automatically on GitHub Actions for every push and pull request.
