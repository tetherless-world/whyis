# Autonomic Agent Component Tests

This directory contains component tests for Whyis autonomic agents. These tests use the `AgentUnitTestCase` base class which provides an in-memory app infrastructure for testing agent behavior.

## Test Infrastructure

### AgentUnitTestCase

The `AgentUnitTestCase` class (from `whyis.test.agent_unit_test_case`) provides:
- An in-memory Flask application with test configuration
- In-memory RDF database for testing
- Nanopublication manager for test data
- `run_agent()` method to execute agents in a controlled environment
- `dry_run` flag to prevent actual database modifications during testing

### Running These Tests

These component tests require the full Whyis environment with all dependencies installed. They are designed to run in the Docker environment or with a complete Whyis installation.

#### Using Docker (Recommended)
```bash
# Run all agent tests
docker run whyis:latest python3 manage.py test --test=tests/unit/whyis_test/autonomic

# Run specific test file
docker run whyis:latest python3 manage.py test --test=tests/unit/whyis_test/autonomic/test_crawler
```

#### With Full Installation
```bash
# From whyis root directory
python manage.py test --test=tests/unit/whyis_test/autonomic
```

## Test Files

### test_cache_updater.py
Tests the `CacheUpdater` agent which maintains cached views of resources.

**Key Tests:**
- Agent initialization and configuration
- Input/output class validation
- Cache update processing with nanopublications

### test_crawler.py
Tests the `Crawler` agent which traverses linked data graphs.

**Key Tests:**
- Crawler initialization with depth and predicates
- Custom node type configuration
- Graph traversal with nanopublications
- Query generation

### test_dataset_importer.py
Tests the `DatasetImporter` agent which imports dataset entities.

**Key Tests:**
- Agent initialization
- Dataset entity processing
- Dry run mode behavior

### test_deductor.py
Tests the `Deductor` agent which performs inference/deduction.

**Key Tests:**
- Deduction rule processing
- Inference with ontology definitions
- Dry run mode

### test_frir_agent.py (Existing)
Tests the FRIR (File Resource Information Resource) archiver agent.

### test_ontology_importer.py (Existing)
Tests the ontology importing agent.

### test_setlr_agents.py (Existing)
Tests SETL-based ETL agents.

## Writing New Agent Tests

To create a new agent test:

1. Inherit from `AgentUnitTestCase`:
```python
from whyis.test.agent_unit_test_case import AgentUnitTestCase

class MyAgentTestCase(AgentUnitTestCase):
    pass
```

2. Create test RDF data:
```python
test_data = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# ... your test data
"""
```

3. Write test methods:
```python
def test_my_agent(self):
    self.dry_run = False  # Set to True to prevent DB changes
    
    # Create nanopublication with test data
    np = nanopub.Nanopublication()
    np.assertion.parse(data=test_data, format="turtle")
    
    # Initialize agent
    agent = autonomic.MyAgent()
    
    # Prepare and publish
    nanopubs = self.app.nanopub_manager.prepare(np)
    self.app.nanopub_manager.publish(*nanopubs)
    
    # Run agent
    results = self.run_agent(agent)
    
    # Assert expected behavior
    assert len(results) > 0
```

## Test Patterns

### Testing Agent Configuration
```python
def test_agent_initialization(self):
    agent = autonomic.MyAgent()
    assert agent is not None
    assert hasattr(agent, 'activity_class')
```

### Testing Input/Output Classes
```python
def test_agent_input_class(self):
    agent = autonomic.MyAgent()
    input_class = agent.getInputClass()
    assert input_class == ExpectedClass
```

### Testing With Nanopublications
```python
def test_agent_with_nanopub(self):
    self.dry_run = False
    np = nanopub.Nanopublication()
    np.assertion.parse(data=test_rdf, format="turtle")
    
    agent = autonomic.MyAgent()
    nanopubs = self.app.nanopub_manager.prepare(np)
    self.app.nanopub_manager.publish(*nanopubs)
    
    results = self.run_agent(agent)
    assert isinstance(results, list)
```

### Testing Dry Run Mode
```python
def test_agent_dry_run(self):
    self.dry_run = True
    agent = autonomic.MyAgent()
    agent.dry_run = True
    
    results = self.run_agent(agent, nanopublication=np)
    # Verify no database changes
```

## Dependencies

These tests require:
- Full Whyis installation with all dependencies
- Flask and Flask extensions
- RDFlib
- SADI
- SETLR
- Depot (file storage)
- All agent-specific dependencies

## Notes

- Component tests are slower than unit tests due to app initialization
- Use `dry_run=True` when testing logic without database changes
- Tests are isolated - each test gets a fresh in-memory database
- Some agents may require specific configuration or external resources
- CI/CD runs these tests in Docker with all dependencies available
