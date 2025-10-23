# Vue.js Unit Testing

This directory contains unit tests for the Whyis Vue.js components and utilities.

## Test Framework

- **Jest** - JavaScript testing framework
- **@vue/test-utils** - Official unit testing utility library for Vue.js
- **babel-jest** - Babel transformer for Jest
- **vue-jest** - Vue SFC transformer for Jest

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

## Test Structure

```
tests/
├── __mocks__/          # Mock files for styles and assets
│   └── styleMock.js
├── components/         # Component tests
│   └── spinner.spec.js
├── mixins/            # Mixin tests
│   └── view-mixin.spec.js
├── modules/           # Module tests
│   └── event-services.spec.js
├── store/             # Vuex store tests
│   └── viz-editor.spec.js
├── utilities/         # Utility function tests
│   ├── common-namespaces.spec.js
│   ├── debounce.spec.js
│   ├── slugs.spec.js
│   └── views.spec.js
└── setup.js           # Test environment setup
```

## Writing Tests

### Utility Function Tests

```javascript
import { myFunction } from '../../js/whyis_vue/utilities/my-module';

describe('myFunction', () => {
  test('should do something', () => {
    expect(myFunction('input')).toBe('output');
  });
});
```

### Vue Component Tests

```javascript
import { createLocalVue, shallowMount } from '@vue/test-utils';
import MyComponent from '../../js/whyis_vue/components/MyComponent.vue';

describe('MyComponent', () => {
  let localVue;
  
  beforeEach(() => {
    localVue = createLocalVue();
  });

  test('should render correctly', () => {
    const wrapper = shallowMount(MyComponent, { localVue });
    expect(wrapper.exists()).toBe(true);
    wrapper.destroy();
  });
});
```

### Vuex Store Tests

```javascript
import { createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import myModule from '../../js/whyis_vue/store/my-module';

describe('my-module store', () => {
  let localVue;
  let store;

  beforeEach(() => {
    localVue = createLocalVue();
    localVue.use(Vuex);
    
    store = new Vuex.Store({
      modules: {
        myModule: {
          namespaced: true,
          ...myModule
        }
      }
    });
  });

  test('should have correct initial state', () => {
    expect(store.state.myModule).toBeDefined();
  });
});
```

## Coverage

Coverage reports are generated in the `coverage/` directory when running `npm run test:coverage`.

Current coverage focuses on:
- ✅ Utility functions (100% coverage for tested modules)
- ✅ Mixins (100% coverage)
- ✅ Component logic (excluding full component rendering)
- ✅ Vuex store modules (core functionality)

## Continuous Integration

Tests are automatically run in CI via both GitHub Actions and CircleCI:

### GitHub Actions
- **vue-tests.yml** - Runs on every push and pull request to main branches
- **frontend-ci.yml** - Comprehensive CI with linting, testing on Node 18.x and 20.x
- Automatic coverage reporting and artifact uploads
- Status badges visible in main README.md

### CircleCI
- Tests run in Docker containers via `.circleci/test-vue.sh`
- Integrated into existing CircleCI pipeline (`.circleci/config.yml`)
- Runs after Python unit tests in the build process

## Mocking

### Global Window Objects

The `tests/setup.js` file sets up global window objects used by Whyis components:
- `window.NODE_URI`
- `window.ROOT_URL`
- `window.LOD_PREFIX`
- `window.USER`

### External Dependencies

Complex external dependencies (like vega-chart utilities) are mocked in individual test files using Jest's `jest.mock()` function.

## Best Practices

1. **Test behavior, not implementation** - Focus on what the code does, not how it does it
2. **Use descriptive test names** - Test names should clearly describe what is being tested
3. **Keep tests focused** - Each test should verify one specific behavior
4. **Use beforeEach/afterEach** - Set up and clean up test state properly
5. **Mock external dependencies** - Isolate the code being tested from external dependencies
6. **Maintain high coverage** - Aim for >80% coverage on new code

## Known Limitations

- Full Vue component rendering tests are limited due to ES6 module import complexities
- Component logic is tested separately from templates
- Coverage collection for `.vue` files is disabled to avoid Babel version conflicts

## Adding New Tests

When adding new Vue.js code, please add corresponding tests:

1. Create a new test file in the appropriate directory
2. Follow existing test patterns
3. Ensure all tests pass before committing
4. Verify coverage hasn't decreased significantly

## Troubleshooting

### Tests fail with "Cannot use import statement outside a module"

This usually means Jest isn't transforming the file correctly. Check:
- The file extension is included in `jest.config.cjs` `moduleFileExtensions`
- The appropriate transformer is configured in `transform`

### Mock not working

Ensure mocks are defined before importing the module being tested:

```javascript
jest.mock('../../path/to/module', () => ({
  // mock implementation
}));

import MyComponent from '../../path/to/component';
```

### JSDOM errors

Some browser APIs aren't fully implemented in JSDOM. Use mocks or stubs for:
- `window.location` navigation
- Complex DOM APIs
- Browser-specific features
