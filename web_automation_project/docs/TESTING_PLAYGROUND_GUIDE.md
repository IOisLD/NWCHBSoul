# Testing Playground Setup Guide

## What is the Testing Playground?

The **Testing Playground** is a "virtual hologram" (local, lightweight replica) of the live Jiffy website. It allows you to:

- **Test safely** — No risk to the live site
- **Iterate rapidly** — Experiment with automation, UI changes, data scenarios
- **Understand the system** — Deep dive into API contracts, data structures, and workflows
- **Reproduce issues** — Create isolated test cases for debugging

## Architecture

```
┌─────────────────────────────────────────────────────┐
│       Your Local Machine (Safe Sandbox)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │   Mock API Server (Flask)                    │  │
│  │   - Port 5000                                │  │
│  │   - Serves JSON from fixtures/               │  │
│  │   - Logs all requests for debugging          │  │
│  └──────────────────────────────────────────────┘  │
│           ▲                                         │
│           │ (API calls)                            │
│           │                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │   Local Frontend (Optional)                  │  │
│  │   - Downloaded HTML/CSS/JS                   │  │
│  │   - Rewired to call localhost:5000           │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │   Your Automation Scripts                    │  │
│  │   - Point to http://localhost:5000           │  │
│  │   - Test crawl, scrape, replay workflows     │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│       Live Site (No Changes)                        │
│  https://jiffy.secondavenue.com                     │
│  (You only visit to capture data initially)         │
└─────────────────────────────────────────────────────┘
```

## Quick Start (5 Minutes)

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
python -m playwright install
```

### 2. Start Mock API Server

```powershell
# In Terminal 1
cd c:\Users\GCS\NWCHBSoul\web_automation_project
.\playground\start_playground.ps1
```

Or manually:
```powershell
python -m scripts.mock_api_server --port 5000 --fixtures-dir playground/api_fixtures
```

You should see:
```
[2025-11-27 14:30:00] MockAPI - INFO - Starting Mock API Server on 127.0.0.1:5000
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: login
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: api_residents
...
 * Running on http://127.0.0.1:5000
```

### 3. Verify It's Working

```powershell
# In Terminal 2
curl http://localhost:5000/mock-api/health

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2025-11-27T14:30:00.000000",
#   "fixtures_loaded": 4,
#   "requests_logged": 0
# }
```

### 4. Run a Quick Test

```powershell
# In Terminal 2
python -m pytest tests/test_playground.py::TestMockAPIServer::test_server_health -v

# Expected: PASSED
```

## Use Cases & Workflows

### Use Case 1: Test Your Automation Script Locally

**Goal:** Make sure your web scraper/crawler works without hitting the live site.

**Steps:**

1. Start the mock server (see Quick Start above).
2. Point your automation to `http://localhost:5000`:

```python
# scripts/test_automation_safe.py
import requests

BASE_URL = 'http://localhost:5000'

# Login to mock server
response = requests.post(f'{BASE_URL}/login', json={
    'email': 'admin@jiffy.local',
    'password': 'test'
})
print(f"✓ Login successful: {response.json()['user']['name']}")

# Fetch residents
response = requests.get(f'{BASE_URL}/api/residents')
residents = response.json()['residents']
print(f"✓ Found {len(residents)} residents")

# Process payment for first resident
resident_id = residents[0]['id']
response = requests.put(f'{BASE_URL}/api/residents/{resident_id}/payment', json={
    'amount': 100
})
print(f"✓ Payment processed: {response.json()['transaction_id']}")
```

**Run it:**
```powershell
python scripts/test_automation_safe.py
```

### Use Case 2: Test Error Scenarios

**Goal:** Verify your automation handles API errors gracefully.

**Steps:**

1. Create an error fixture file at `playground/api_fixtures/api_residents_error.json`:

```json
{
  "status": 500,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "success": false,
    "error": "Database connection failed",
    "error_code": "DB_ERROR"
  }
}
```

2. Stop and restart the mock server (it will load the new fixture).
3. Test your error handling:

```python
# scripts/test_error_handling.py
import requests

response = requests.get('http://localhost:5000/api/residents')
if response.status_code >= 400:
    print(f"✓ Handled error correctly: {response.json()['error']}")
```

### Use Case 3: Simulate Different User Roles/Data

**Goal:** Test multiple scenarios without modifying the live database.

**Steps:**

1. Create multiple fixture sets:
   - `playground/api_fixtures_admin/` (admin user response)
   - `playground/api_fixtures_user/` (regular user response)
   - `playground/api_fixtures_readonly/` (read-only user response)

2. Start servers on different ports:

```powershell
# Terminal 1: Admin scenario
python -m scripts.mock_api_server --port 5001 --fixtures-dir playground/api_fixtures_admin

# Terminal 2: Regular user scenario
python -m scripts.mock_api_server --port 5002 --fixtures-dir playground/api_fixtures_user
```

3. Run tests against each:

```python
def test_admin_access():
    response = requests.get('http://localhost:5001/api/admin/reports')
    assert response.status_code == 200

def test_user_access():
    response = requests.get('http://localhost:5002/api/admin/reports')
    assert response.status_code == 403  # Forbidden
```

### Use Case 4: Modify Frontend & Test UI Changes

**Goal:** Redesign the web interface without touching the live site.

**Steps:**

1. Download the frontend:

```powershell
python -m scripts.download_frontend --url https://jiffy.secondavenue.com --output playground/frontend
```

2. Edit the HTML, CSS, or JavaScript files locally:

```html
<!-- playground/frontend/index.html -->
<!-- Change button color -->
<button style="background-color: green;">SIGN IN</button>
```

3. Open the local file and test:

```powershell
# Open in browser
start file:///C:\Users\GCS\NWCHBSoul\web_automation_project\playground\frontend\index.html
```

4. The page will call `http://localhost:5000` for API data.

### Use Case 5: Run Integration Tests

**Goal:** Verify the entire workflow (login → scrape → process) works end-to-end.

**Steps:**

1. Start the mock server.
2. Run the integration tests:

```powershell
python -m pytest tests/test_playground.py::TestPlaygroundScenarios -v
```

**Output:**
```
test_full_login_and_resident_retrieval PASSED
test_select_resident_and_process_payment PASSED
```

## Advanced: How the Mock Server Works

### Fixture Matching Algorithm

When you make a request to the mock server, it tries to find a matching fixture:

1. **Normalize the path:** `/api/residents/1` → `api_residents_1`
2. **Try exact match:** Is there a file `api_residents_1.json`?
3. **Try method prefix:** Is there a file `put_api_residents_1.json` (for PUT requests)?
4. **Try partial match:** Does any fixture filename contain `api_residents_1`?

### Example

```
Request:  PUT /api/residents/1/payment
Fixture lookup:
  1. Check: put_api_residents_1_payment.json  ✓ FOUND!
  2. (Match found, return fixture)
```

### Request Logging

All requests are logged and accessible via the `/mock-api/request-log` endpoint:

```powershell
curl http://localhost:5000/mock-api/request-log | python -m json.tool

# Output:
# {
#   "total": 5,
#   "requests": [
#     {
#       "timestamp": "2025-11-27T14:30:00.000000",
#       "method": "POST",
#       "path": "/login",
#       "query": "",
#       "body_preview": "{\"email\": \"admin@jiffy.local\", \"password\": \"test\"}",
#       "headers": { ... }
#     },
#     ...
#   ]
# }
```

## Fixture Structure Reference

### Standard Fixture Format

```json
{
  "status": 200,
  "headers": {
    "Content-Type": "application/json",
    "X-Custom-Header": "value"
  },
  "body": {
    "success": true,
    "data": { ... }
  }
}
```

### Common HTTP Status Codes

- `200` — Success
- `201` — Created
- `400` — Bad request
- `401` — Unauthorized
- `403` — Forbidden
- `404` — Not found
- `500` — Server error
- `503` — Service unavailable

### Response Headers Reference

Common headers to include:

```json
{
  "Content-Type": "application/json",
  "Content-Length": "1024",
  "Cache-Control": "max-age=3600",
  "X-API-Version": "1.0",
  "X-RateLimit-Limit": "1000",
  "X-RateLimit-Remaining": "999"
}
```

## Debugging & Troubleshooting

### Server Won't Start

```
ERROR: Address already in use
```

**Solution:** Change the port:
```powershell
python -m scripts.mock_api_server --port 5001
```

### Fixtures Not Loading

```
WARNING: Fixtures directory not found
```

**Solution:** Check the path:
```powershell
Test-Path playground/api_fixtures

# Create if missing
mkdir playground/api_fixtures
```

### Request Returns 404

**Cause:** No matching fixture found.

**Debug:**
```powershell
# Check what fixtures are loaded
curl http://localhost:5000/mock-api/fixtures

# Check the request log
curl http://localhost:5000/mock-api/request-log
```

**Solution:** Create the missing fixture file with the correct naming convention.

### My Test Still Calls the Live Site

**Cause:** You didn't update the base URL in your automation script.

**Fix:**
```python
# Before (live site)
BASE_URL = 'https://jiffy.secondavenue.com'

# After (local playground)
BASE_URL = 'http://localhost:5000'
```

## Next Steps

1. **Capture Real Data:**
   - Run `scripts.crawl_scrape_runner` against the live site.
   - Extract responses from `results/api_captures_enhanced.json`.
   - Create corresponding fixture files in `playground/api_fixtures/`.

2. **Download Frontend:**
   - Run `scripts.download_frontend` to get HTML/CSS/JS.
   - Edit and test UI changes locally.

3. **Write Integration Tests:**
   - Use `tests/test_playground.py` as a template.
   - Add your own test scenarios.
   - Run `pytest tests/test_playground.py`.

4. **Automate Workflows:**
   - Write a script that logs in, scrapes data, processes payments.
   - Test it against the mock server first.
   - When confident, point it at the live site.

## Key Takeaway

**The Testing Playground is your sandbox.** You can:
- ✓ Break things safely
- ✓ Experiment freely
- ✓ Learn the system deeply
- ✓ Iterate rapidly
- ✓ Test edge cases
- ✗ Never affect the live site

Use it to build confidence in your automation before deploying to production.

---

For more details, see:
- `playground/README_PLAYGROUND.md` — Quick reference
- `scripts/mock_api_server.py` — Server implementation
- `tests/test_playground.py` — Example tests
