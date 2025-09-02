# Vue.js Testing Guide

This directory contains unit tests and integration tests for the Vue.js components in the Whyis application.

## Testing Framework

- **Vitest**: Modern testing framework with Vite integration
- **Vue Test Utils**: Official Vue.js testing utilities 
- **jsdom**: DOM implementation for testing
- **@vitest/coverage-v8**: Code coverage reporting

## Directory Structure

```
tests/
├── setup.js                 # Global test configuration
├── helpers/
│   └── test-utils.js        # Testing utility functions
└── unit/
    ├── spinner.test.js      # Spinner component tests (✓ 13 tests)
    ├── dialog.test.js       # Dialog component tests 
    ├── search-autocomplete.test.js  # Search component tests
    ├── upload-knowledge.test.js     # Upload dialog tests
    ├── vega-lite-wrapper.test.js    # Chart visualization tests
    └── template-integration.test.js # Template usage pattern tests
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests once (for CI)
npm run test:run

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test:run js/whyis_vue/tests/unit/spinner.test.js
```

## Test Categories

### 1. Component Unit Tests

Tests individual Vue components in isolation:

- **Rendering**: Component structure and props
- **Props**: Input validation and default values
- **Methods**: Component logic and functionality
- **Events**: Event emission and handling
- **Data**: Component state management

### 2. Template Integration Tests

Tests how components are used in Jinja2 templates:

- **base_vue.html**: Navigation components (search, upload, etc.)
- **chart_edit.html**: Visualization editor components
- **Form Integration**: Component integration with HTML forms
- **Event Handling**: Template-bound event handlers
- **Material Design**: vue-material component usage

### 3. Template Usage Scenarios

Tests based on actual template usage patterns:

- Component prop binding from template variables
- Event handling with `.sync` modifiers
- Form integration and validation
- SPARQL query integration
- Global component registration

## Test Utilities

### `test-utils.js`

Helper functions for component testing:

- `mountComponent()`: Full component mounting
- `shallowMountComponent()`: Shallow component mounting
- `createTestVue()`: Local Vue instance with Material Design
- `mockProps`: Common mock props for testing
- `flushPromises()`: Async test utilities

### `setup.js`

Global test configuration:

- Vue Material Design setup
- Global mocks (axios, window, etc.)
- Template variable mocks (USER, NODE_URI, etc.)

## Component Test Examples

### Basic Component Test

```javascript
import { describe, it, expect } from 'vitest';
import { shallowMountComponent } from '../helpers/test-utils.js';
import MyComponent from '../../components/my-component.vue';

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = shallowMountComponent(MyComponent, {
      propsData: { prop: 'value' }
    });

    expect(wrapper.find('.my-element').exists()).toBe(true);
  });
});
```

### Template Integration Test

```javascript
it('integrates with template form', () => {
  // Test how component is used in base_vue.html
  const wrapper = shallowMountComponent(SearchAutocomplete);
  
  // Should have form integration elements
  expect(wrapper.find('input[name="search"]').exists()).toBe(true);
});
```

## Mocking Strategies

### External Dependencies

- **axios**: Mocked for HTTP requests
- **vega-embed**: Mocked for chart rendering
- **vega-lite schema**: Mocked to avoid URL resolution
- **window.location**: Mocked for navigation testing

### Template Variables

Global variables from templates are mocked in `setup.js`:

- `NODE_URI`: Current resource identifier
- `USER`: Current user information
- `NAVIGATION`: Navigation state
- `ROOT_URL`: Application root URL

## Coverage Reports

Coverage reports are generated in the `coverage/` directory:

- **HTML Report**: `coverage/index.html`
- **JSON Report**: `coverage/coverage.json`
- **Text Summary**: Console output

## CI Integration

Tests are integrated with CircleCI:

- **test-js**: Runs JavaScript tests with coverage
- **lint-js**: Runs ESLint on JavaScript code
- Results stored as artifacts and test results

## Best Practices

### Writing Tests

1. **Focus on behavior**: Test what the component does, not how it does it
2. **Template-driven**: Base tests on actual template usage patterns
3. **Minimal mocking**: Only mock external dependencies
4. **Clear assertions**: Use descriptive test names and assertions

### Test Structure

1. **Arrange**: Set up component with props/data
2. **Act**: Trigger the behavior being tested
3. **Assert**: Verify the expected outcome

### Template Integration

1. **Props binding**: Test component prop integration with template variables
2. **Event handling**: Test event emission and template event handlers
3. **Form integration**: Test component integration with HTML forms
4. **Styling**: Test Material Design component usage

## Troubleshooting

### Common Issues

1. **Mock problems**: Check `setup.js` for global mocks
2. **Vue Material**: Ensure components are properly imported
3. **Async tests**: Use `flushPromises()` for async operations
4. **Template attributes**: Use correct attribute syntax for Vue directives

### Debug Tips

1. Use `wrapper.html()` to inspect rendered output
2. Use `console.log(wrapper.vm)` to inspect component instance
3. Check browser console for Vue warnings
4. Verify mock setup in test files

## Contributing

When adding new components:

1. **Create unit tests**: Test component in isolation
2. **Add integration tests**: Test template usage patterns
3. **Update test utilities**: Add common props/mocks if needed
4. **Document usage**: Add examples to this README

For test fixes:

1. **Identify the issue**: Component logic vs. test assumptions
2. **Fix the root cause**: Update component or test appropriately
3. **Verify coverage**: Ensure new code paths are tested
4. **Test integration**: Verify template usage still works