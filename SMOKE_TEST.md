# Whyis Smoke Test Documentation

This document describes the smoke testing setup for the Whyis knowledge graph framework, designed to detect Vue 3 migration issues and ensure the frontend renders correctly without "[object Promise]" errors.

## Overview

The smoke test system consists of two main components:

1. **GitHub Actions CI Workflow** (`.github/workflows/smoke-test.yml`) - Automated frontend testing
2. **Manual Full Smoke Test Script** (`full_smoke_test.sh`) - Complete application testing

## GitHub Actions CI Workflow

### Purpose
Automatically tests the frontend build and checks for Vue 3 compatibility issues on every push and pull request.

### What it checks:
- ✅ Frontend builds successfully with `npm run build-dev`
- ✅ No Vue Material components that cause "[object Promise]" issues
- ✅ No deprecated Vue 2 `.sync` syntax
- ✅ Required build artifacts are generated (`whyis.js`, `whyis.css`)

### Running automatically:
The workflow runs automatically on pushes to `main`/`master` branches and on pull requests.

### Viewing results:
- Check the "Actions" tab in GitHub
- Look for the "Whyis Frontend Smoke Test" workflow
- Download build artifacts if needed for debugging

## Manual Full Smoke Test

### Purpose
Performs a complete end-to-end test of the Whyis application, including:
- Building and installing the Python package
- Starting the Whyis server
- Testing the web interface with a browser
- Checking for JavaScript console errors
- Verifying no "[object Promise]" rendering issues

### Usage

```bash
# From the Whyis project root directory:
./full_smoke_test.sh
```

### Requirements
- Python 3.9+ (Python 3.12 recommended)
- Node.js 18+
- Git repository (for build detection)
- Available port 5000
- Internet connection (for downloading dependencies)

### What the script does:

1. **Environment Setup**
   - Creates a Python virtual environment
   - Installs build dependencies (`requests`, `wheel`, `setuptools`)

2. **Package Building**
   - Runs `python setup.py dist` (if available)
   - Installs package with `pip install -e .`

3. **Test Environment**
   - Creates `test_kgapp` directory
   - Installs Playwright for browser testing

4. **Server Testing**
   - Starts Whyis server with `whyis run --threaded`
   - Waits for server to be ready (up to 60 seconds)

5. **Browser Testing**
   - Tests HTTP connectivity
   - Launches headless browser
   - Navigates to http://localhost:5000
   - Checks for:
     - Vue app initialization (`#app` element)
     - Navigation elements
     - "[object Promise]" text (critical failure)
     - JavaScript console errors
     - Network request failures

6. **Results**
   - Provides detailed test results
   - Takes screenshots for visual verification
   - Returns appropriate exit code (0=success, 1=failure)

### Example successful output:

```
=== COMPREHENSIVE SMOKE TEST ===
1. Testing HTTP connectivity...
   ✓ HTTP status: 200
2. Launching browser for detailed testing...
3. Navigating to homepage...
4. Waiting for page to load completely...
5. Taking screenshot...
6. Page title: 'Whyis Knowledge Graph'
7. Checking Vue app initialization...
   ✓ Vue app element (#app) found
8. Checking navigation elements...
   ✓ Found 1 navigation element(s)
9. Checking for Vue rendering issues...
   ✓ No '[object Promise]' rendering issues found

=== SMOKE TEST RESULTS ===
✅ SMOKE TEST PASSED: No critical issues detected
   The application appears to be working correctly!
```

## Troubleshooting

### Common Issues

**Build Failures:**
- Ensure you're in the Whyis project root directory
- Check that Node.js and npm are properly installed
- Verify `whyis/static/package.json` exists

**Server Start Failures:**
- Ensure port 5000 is available
- Check Python dependencies are installed correctly
- Verify Redis server is running (if required)

**"[object Promise]" Errors:**
- These indicate Vue Material components that aren't compatible with Vue 3
- Check for components like `md-dialog`, `md-button`, `md-field`, etc.
- Replace with Bootstrap equivalents

**Browser Test Failures:**
- Ensure Playwright is installed: `playwright install chromium`
- Check console output for specific JavaScript errors
- Review screenshot files in test directory

### Debug Mode

To run the browser test in non-headless mode for debugging:

1. Edit `full_smoke_test.sh`
2. Find the line: `browser = await p.chromium.launch(headless=True)`
3. Change to: `browser = await p.chromium.launch(headless=False)`
4. Run the script to see the browser window

## Expected Page Appearance

The smoke test checks that the Whyis homepage loads correctly and should show:
- Clean Whyis interface
- Navigation elements
- No "[object Promise]" text anywhere
- No JavaScript console errors

The expected appearance should match the screenshot provided in the GitHub issue.

## Maintenance

### Updating the Test
When adding new Vue components or changing the frontend architecture:

1. Update the CI workflow if new file patterns need checking
2. Modify the smoke test script if new critical elements need verification
3. Update this documentation with any new requirements or troubleshooting steps

### Adding New Checks
To add new smoke test validations:

1. Edit the `comprehensive_smoke_test.py` script generated by `full_smoke_test.sh`
2. Add new checks in the browser testing section
3. Update the results reporting section