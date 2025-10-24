# Testing Framework Documentation

## Overview

The Whyis project uses **pytest** as its primary testing framework for Python code. This replaces the deprecated `nose` framework that was previously used.

## Test Structure

Tests are organized in the `tests/` directory with the following structure:

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── __init__.py
├── api/                  # API endpoint tests
│   ├── test_*.py
│   └── view/
├── integration/          # Integration tests
│   └── test_*.py
└── unit/                 # Unit tests
    └── test_*.py
```

## Running Tests

### Prerequisites

Install testing dependencies:

```bash
pip install pytest pytest-flask pytest-cov pytest-mock coverage flask-testing
```

Or install all dependencies including test requirements:

```bash
pip install -e ".[test]"
```

### Basic Test Commands

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit/
```

Run API tests only:
```bash
pytest tests/api/
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/unit/test_namespace.py
```

Run specific test class or function:
```bash
pytest tests/unit/test_namespace.py::TestNamespaceContainer
pytest tests/unit/test_namespace.py::TestNamespaceContainer::test_namespace_container_has_rdf
```

### Coverage Reports

Run tests with coverage:
```bash
pytest --cov=whyis --cov-report=html --cov-report=term
```

The HTML coverage report will be in `htmlcov/index.html`.

Generate XML coverage for CI:
```bash
pytest --cov=whyis --cov-report=xml
```

### Test Options

Run tests and stop at first failure:
```bash
pytest -x
```

Run only tests that failed in last run:
```bash
pytest --lf
```

Run in parallel (requires pytest-xdist):
```bash
pytest -n auto
```

### Watch Mode

For development, you can use pytest-watch:
```bash
pip install pytest-watch
ptw
```

## Writing Tests

### Test Discovery

Pytest automatically discovers tests based on naming conventions:
- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Unit Test

```python
"""
Unit tests for whyis.module_name.

Tests the functionality of module_name.
"""

import pytest
from whyis.module_name import function_to_test


class TestFunctionName:
    """Test the function_to_test function."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = function_to_test("input")
        assert result == "expected_output"
    
    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py` or test files:

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}


def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["key"] == "value"
```

### Common Fixtures

The following fixtures are available from `tests/conftest.py`:

- `app`: Flask application instance
- `client`: Test client for making requests
- `runner`: CLI runner for testing commands
- `test_config`: Test configuration dictionary

### Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_unit_function():
    """A unit test."""
    pass

@pytest.mark.slow
def test_slow_function():
    """A slow-running test."""
    pass

@pytest.mark.skipif_ci
def test_skip_in_ci():
    """Test skipped in CI environment."""
    pass
```

Run only tests with specific marker:
```bash
pytest -m unit
```

Skip tests with specific marker:
```bash
pytest -m "not slow"
```

## Test Configuration

### pytest.ini

Main pytest configuration is in `pytest.ini`:

```ini
[pytest]
python_files = test_*.py *_test.py
python_classes = Test* *Tests *TestCase
python_functions = test_*
testpaths = tests
minversion = 6.0
addopts = --verbose --strict-markers --tb=short -ra
```

### Coverage Configuration

Coverage settings are also in `pytest.ini`:

```ini
[coverage:run]
branch = True
source = whyis
omit = 
    */test/*
    */tests/*
    */__pycache__/*
    */venv/*
```

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Every push to main/master/develop branches
- Every pull request to main/master/develop branches
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

See `.github/workflows/python-tests.yml` for CI configuration.

## Best Practices

1. **One assertion per test**: Keep tests focused and simple
2. **Descriptive names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly:
   ```python
   def test_function():
       # Arrange
       input_data = prepare_data()
       
       # Act
       result = function_to_test(input_data)
       
       # Assert
       assert result == expected_value
   ```
4. **Use fixtures**: Share setup code via fixtures
5. **Test edge cases**: Don't just test the happy path
6. **Keep tests isolated**: Tests should not depend on each other
7. **Mock external dependencies**: Use `pytest-mock` for mocking
8. **Document tests**: Add docstrings explaining what's being tested

## Troubleshooting

### Import Errors

If you get import errors, make sure the package is installed:
```bash
pip install -e .
```

### Missing Dependencies

Install test dependencies:
```bash
pip install pytest pytest-flask pytest-cov pytest-mock
```

### Test Not Discovered

Check that:
- File name starts with `test_` or ends with `_test.py`
- Class name starts with `Test`
- Function name starts with `test_`
- File has `__init__.py` in parent directories

### CI Environment

Tests may behave differently in CI. Use the `CI` environment variable:

```python
import os
import pytest

@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Skip in CI")
def test_local_only():
    pass
```

## Coverage Goals

Current test coverage by module:

| Module | Coverage | Tests |
|--------|----------|-------|
| whyis.namespace | 100% | 36 tests |
| whyis.data_formats | 100% | 17 tests |
| whyis.data_extensions | 100% | 22 tests |
| whyis.html_mime_types | 100% | 10 tests |
| whyis._version | 100% | 12 tests |

**Total**: 97 unit tests covering core utility modules

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Flask Documentation](https://pytest-flask.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contributing Tests

When adding new features or fixing bugs:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before submitting PR
3. Aim for >80% code coverage on new code
4. Update this documentation if adding new test patterns
5. Use existing tests as examples for style and structure

## Contact

For questions about testing, see the main project README or open an issue on GitHub.
