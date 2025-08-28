#!/bin/bash

# Whyis Full Smoke Test Script
# This script performs the complete smoke test as requested by the maintainer
# It sets up a venv, builds, installs, and tests the Whyis application
# Usage: ./full_smoke_test.sh

set -e

echo "=== Whyis Full Smoke Test ==="
echo "This script will set up a virtual environment, build and install Whyis,"
echo "start the server, and test for console errors and rendering issues."
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: This script must be run from the Whyis project root directory"
    exit 1
fi

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    if [ ! -z "$WHYIS_PID" ] && kill -0 $WHYIS_PID 2>/dev/null; then
        echo "Stopping Whyis server (PID: $WHYIS_PID)..."
        kill $WHYIS_PID || true
        sleep 2
        # Force kill if still running
        if kill -0 $WHYIS_PID 2>/dev/null; then
            kill -9 $WHYIS_PID || true
        fi
    fi
}

# Set up cleanup on exit
trap cleanup EXIT

echo "1. Setting up Python virtual environment..."
if [ -d "venv" ]; then
    echo "   Removing existing venv..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

echo "2. Installing build dependencies..."
pip install --upgrade pip
pip install requests wheel setuptools

echo "3. Building and installing Whyis package..."
# Try the build command first (as requested)
if python setup.py dist 2>/dev/null; then
    echo "   Build completed successfully"
else
    echo "   Build command failed, continuing with pip install..."
fi

# Install the package
pip install -e .

echo "4. Creating test knowledge graph directory..."
TEST_DIR="test_kgapp"
if [ -d "$TEST_DIR" ]; then
    rm -rf "$TEST_DIR"
fi
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "5. Installing Playwright for browser testing..."
pip install playwright requests
playwright install chromium

echo "6. Starting Whyis server..."
whyis run --threaded &
WHYIS_PID=$!
echo "   Server started with PID: $WHYIS_PID"

# Wait for server to start
echo "7. Waiting for server to be ready..."
MAX_WAIT=60
for i in $(seq 1 $MAX_WAIT); do
    if curl -sf http://localhost:5000 >/dev/null 2>&1; then
        echo "   Server is ready! (took ${i}s)"
        break
    fi
    if [ $i -eq $MAX_WAIT ]; then
        echo "   ERROR: Server failed to start within ${MAX_WAIT} seconds"
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

echo "8. Running browser smoke test..."

# Create comprehensive smoke test script
cat > comprehensive_smoke_test.py << 'EOF'
import asyncio
import sys
import time
from playwright.async_api import async_playwright
import requests

async def run_comprehensive_smoke_test():
    """
    Comprehensive smoke test that checks:
    1. Server responds to HTTP requests
    2. Homepage loads without JavaScript errors
    3. No "[object Promise]" rendering issues
    4. Vue app initializes properly
    5. Navigation elements are present
    6. Takes screenshot for visual verification
    """
    
    print("=== COMPREHENSIVE SMOKE TEST ===")
    
    # First test basic HTTP connectivity
    print("1. Testing HTTP connectivity...")
    try:
        response = requests.get("http://localhost:5000", timeout=10)
        print(f"   ✓ HTTP status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ❌ Expected status 200, got {response.status_code}")
            return 1
    except Exception as e:
        print(f"   ❌ HTTP request failed: {e}")
        return 1
    
    # Now test with browser
    print("2. Launching browser for detailed testing...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        # Collect all console messages and errors
        console_messages = []
        js_errors = []
        network_failures = []
        
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            })
            
        def handle_page_error(error):
            js_errors.append(str(error))
            
        def handle_response(response):
            if response.status >= 400:
                network_failures.append({
                    'url': response.url,
                    'status': response.status
                })
        
        page.on("console", handle_console)
        page.on("pageerror", handle_page_error)
        page.on("response", handle_response)
        
        try:
            print("3. Navigating to homepage...")
            await page.goto("http://localhost:5000", timeout=30000)
            
            print("4. Waiting for page to load completely...")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            print("5. Taking screenshot...")
            await page.screenshot(path="whyis_homepage_test.png", full_page=True)
            
            # Get page title
            title = await page.title()
            print(f"6. Page title: '{title}'")
            
            # Check for Vue app element
            print("7. Checking Vue app initialization...")
            vue_app = await page.query_selector("#app")
            if vue_app:
                print("   ✓ Vue app element (#app) found")
            else:
                print("   ❌ Vue app element (#app) not found")
                js_errors.append("Vue app element (#app) not found")
            
            # Check for navigation
            print("8. Checking navigation elements...")
            nav_elements = await page.query_selector_all("nav, .navbar")
            if len(nav_elements) > 0:
                print(f"   ✓ Found {len(nav_elements)} navigation element(s)")
            else:
                print("   ⚠️  No navigation elements found")
            
            # Critical check: Look for "[object Promise]" text
            print("9. Checking for Vue rendering issues...")
            promise_elements = await page.query_selector_all('text="[object Promise]"')
            if len(promise_elements) > 0:
                print(f"   ❌ CRITICAL: Found {len(promise_elements)} '[object Promise]' rendering issue(s)")
                # Get context around each issue
                for i, elem in enumerate(promise_elements):
                    parent = await elem.evaluate("el => el.parentElement ? el.parentElement.outerHTML : 'no parent'")
                    print(f"      Issue {i+1}: {parent[:200]}...")
                js_errors.append(f"Found {len(promise_elements)} '[object Promise]' rendering issues")
            else:
                print("   ✓ No '[object Promise]' rendering issues found")
            
            # Check for critical JavaScript errors
            print("10. Analyzing console messages...")
            critical_errors = []
            warnings = []
            
            for msg in console_messages:
                if msg['type'] == 'error':
                    # Filter out known non-critical errors
                    msg_text = msg['text'].lower()
                    if not any(skip in msg_text for skip in [
                        'favicon.ico', 
                        'net::err_connection_refused',
                        'failed to load resource',
                        'cors',
                        'mixed content',
                        'manifest'
                    ]):
                        critical_errors.append(msg)
                elif msg['type'] == 'warning':
                    warnings.append(msg)
            
            # Check for network failures
            print("11. Checking network requests...")
            critical_network_failures = [
                f for f in network_failures 
                if not any(ignore in f['url'] for ignore in ['favicon.ico', 'manifest.json'])
            ]
            
            # Report summary
            print("\n=== SMOKE TEST RESULTS ===")
            print(f"Page title: {title}")
            print(f"Total console messages: {len(console_messages)}")
            print(f"JavaScript errors: {len(js_errors)}")
            print(f"Critical console errors: {len(critical_errors)}")
            print(f"Console warnings: {len(warnings)}")
            print(f"Network failures: {len(critical_network_failures)}")
            print(f"Vue rendering issues: {len(promise_elements)}")
            
            # Detailed error reporting
            if critical_errors:
                print("\n📋 Critical console errors:")
                for error in critical_errors:
                    print(f"   - {error['type'].upper()}: {error['text']}")
                    if error['location']:
                        print(f"     Location: {error['location']}")
            
            if js_errors:
                print("\n📋 JavaScript errors:")
                for error in js_errors:
                    print(f"   - {error}")
            
            if critical_network_failures:
                print("\n📋 Network failures:")
                for failure in critical_network_failures:
                    print(f"   - {failure['status']} {failure['url']}")
            
            if warnings:
                print(f"\n📋 Warnings ({len(warnings)} total):")
                for warning in warnings[:5]:  # Show first 5 warnings
                    print(f"   - {warning['text']}")
                if len(warnings) > 5:
                    print(f"   ... and {len(warnings) - 5} more warnings")
            
            # Determine overall result
            has_critical_issues = (
                len(js_errors) > 0 or 
                len(critical_errors) > 0 or 
                len(promise_elements) > 0 or
                len(critical_network_failures) > 0
            )
            
            if has_critical_issues:
                print("\n❌ SMOKE TEST FAILED: Critical issues detected")
                print("   The application has issues that need to be addressed before deployment.")
                return 1
            else:
                print("\n✅ SMOKE TEST PASSED: No critical issues detected")
                print("   The application appears to be working correctly!")
                return 0
                
        except Exception as e:
            print(f"\n❌ SMOKE TEST FAILED: Exception occurred: {e}")
            await page.screenshot(path="whyis_error_test.png", full_page=True)
            return 1
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(run_comprehensive_smoke_test())
    sys.exit(result)
EOF

# Run the comprehensive smoke test
echo "Running comprehensive browser test..."
python comprehensive_smoke_test.py
TEST_RESULT=$?

echo ""
echo "=== SMOKE TEST COMPLETED ==="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ SUCCESS: Whyis application passed all smoke tests!"
    echo ""
    echo "The application is running correctly at http://localhost:5000"
    echo "Screenshots saved in the $TEST_DIR directory for visual verification."
    echo ""
    echo "To view the application:"
    echo "  1. Navigate to http://localhost:5000 in your browser"
    echo "  2. Check that the page matches the expected screenshot"
    echo "  3. Verify there are no console errors in browser dev tools"
else
    echo "❌ FAILURE: Smoke test detected critical issues"
    echo ""
    echo "Please review the error output above and fix the issues."
    echo "Screenshots have been saved in the $TEST_DIR directory for debugging."
fi

echo ""
echo "Smoke test completed with exit code: $TEST_RESULT"
exit $TEST_RESULT