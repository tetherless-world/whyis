# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing and continuous integration.

## Workflows

### vue-tests.yml
Primary Vue.js testing workflow that runs on every push and pull request.

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests targeting these branches

**Steps:**
1. Checkout code
2. Setup Node.js 20.x
3. Install dependencies with npm ci
4. Run Vue.js tests with coverage
5. Upload coverage to Codecov
6. Archive test results as artifacts

**Artifacts:**
- Test coverage reports (available for 30 days)
- Stored in `vue-test-results` artifact

### frontend-ci.yml
Comprehensive frontend CI workflow with matrix testing.

**Triggers:**
- Push to `master`, `main`, or `develop` branches (when frontend files change)
- Pull requests targeting these branches (when frontend files change)

**Matrix:**
- Tests run on Node.js 18.x and 20.x

**Steps:**
1. Checkout code
2. Setup Node.js (matrix version)
3. Install dependencies with npm ci
4. Run ESLint (continues on error)
5. Run Vue.js tests
6. Generate coverage report (Node 20.x only)
7. Upload coverage to Codecov (Node 20.x only)
8. Archive test results
9. Comment on PR with test status (Node 20.x only)

**Artifacts:**
- Test results per Node version (available for 30 days)
- Coverage reports from Node 20.x

## Status Badges

Status badges are displayed in the main README.md:
- Vue.js Tests badge
- Frontend CI badge

## Codecov Integration

Coverage reports are automatically uploaded to Codecov when tests run. This provides:
- Coverage tracking over time
- Coverage diffs on pull requests
- Detailed coverage reports

## Running Locally

To run the same tests that CI runs:

```bash
cd whyis/static
npm install
npm test -- --ci --coverage --maxWorkers=2
```

## Troubleshooting

### Tests fail in CI but pass locally
- Ensure dependencies are installed with `npm install`
- Check Node.js version matches CI (18.x or 20.x)
- Run with `--ci` flag: `npm test -- --ci`

### Artifacts not uploading
- Check workflow permissions in repository settings
- Ensure `actions/upload-artifact@v4` has write permissions
- Verify artifact names don't contain invalid characters

### Coverage not appearing on Codecov
- Verify Codecov token is set in repository secrets (if repo is private)
- Check that coverage files are being generated in correct location
- Review Codecov action logs for upload errors
