# Testing Playground Setup

This directory contains a **"virtual hologram" replica** of the Jiffy website for safe, isolated testing and experimentation.

## Overview

The playground consists of:

1. **Mock API Server** (`scripts/mock_api_server.py`) — Flask app that intercepts API calls and returns mock responses from JSON fixtures.
2. **Frontend Assets** (`playground/frontend/`) — Downloaded HTML, CSS, JS files from the live site, rewritten to use local paths.
3. **API Fixtures** (`playground/api_fixtures/`) — Sample JSON responses (captured or hand-crafted) that the mock server returns.

## Quick Start

### Step 1: Install Dependencies

```powershell
pip install flask flask-cors python-dotenv playwright
python -m playwright install
```

### Step 2: Start the Mock API Server

```powershell
cd c:\Users\GCS\NWCHBSoul\web_automation_project

# Run the mock API server on port 5000
python -m scripts.mock_api_server --port 5000 --fixtures-dir playground/api_fixtures
```

You should see:
```
[2025-11-27 14:30:00] MockAPI - INFO - Starting Mock API Server on 127.0.0.1:5000
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: login
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: api_residents
...
```

### Step 3: Verify the Mock Server is Running

Open a browser or use `curl`:

```powershell
# Check health
curl http://localhost:5000/mock-api/health

# View loaded fixtures
curl http://localhost:5000/mock-api/fixtures

# View request log
curl http://localhost:5000/mock-api/request-log
```

Expected responses:
```json
{
  "status": "ok",
  "timestamp": "2025-11-27T14:30:00.000000",
  "fixtures_loaded": 4,
  "requests_logged": 0
}
```

### Step 4: Test an API Call

```powershell
# This will return the login.json fixture
curl -X POST http://localhost:5000/login

# This will return the api_residents.json fixture
curl http://localhost:5000/api/residents
```

### Step 5: Run Your Automation Against the Playground

From your automation scripts, point API calls to the local mock server:

```python
import requests

# Instead of:
# response = requests.post('https://jiffy.secondavenue.com/login', ...)

# Use:
response = requests.post('http://localhost:5000/login', json={
    'email': 'admin@jiffy.local',
    'password': 'test'
})
print(response.json())  # Returns mock data
```

## Fixture Structure

Each fixture is a JSON file in `playground/api_fixtures/`:

```json
{
  "status": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "success": true,
    "data": { ... }
  }
}
```

### File Naming Convention

- `login.json` → responds to `POST /login`
- `api_residents.json` → responds to `GET /api/residents`
- `api_residents_1.json` → responds to `GET /api/residents/1`
- `put_api_residents_1_payment.json` → responds to `PUT /api/residents/1/payment`

Pattern: `[METHOD]_<path_with_underscores>.json` (method is optional; GET is default)

## Experimentation Workflows

### Scenario 1: Test Your Automation Script

1. Start the mock server (Step 2 above).
2. Point your automation script to `http://localhost:5000` instead of the live site.
3. Run your script — no risk to the live site.

```python
# scripts/test_automation_on_playground.py
import requests

BASE_URL = 'http://localhost:5000'

# Mock login
response = requests.post(f'{BASE_URL}/login', json={
    'email': 'admin@jiffy.local',
    'password': 'test'
})
print(f"Login: {response.json()}")

# Get residents
response = requests.get(f'{BASE_URL}/api/residents')
print(f"Residents: {response.json()}")

# Update resident payment
response = requests.put(f'{BASE_URL}/api/residents/1/payment', json={
    'amount': 500
})
print(f"Payment: {response.json()}")
```

### Scenario 2: Test Edge Cases

Edit the fixture JSON files to simulate error responses, missing data, or unusual scenarios:

**Edit `playground/api_fixtures/api_residents.json` to simulate an error:**
```json
{
  "status": 500,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "success": false,
    "error": "Database connection failed"
  }
}
```

Then restart the mock server and test how your automation handles errors.

### Scenario 3: Modify Frontend & Test Locally

1. Download frontend assets using `scripts/download_frontend.py` (saves to `playground/frontend/`).
2. Edit the HTML/CSS/JS files to test new UI designs.
3. Open `playground/frontend/index.html` in your browser.
4. The page will call `http://localhost:5000` for API data (if configured correctly).

```powershell
# Download frontend from live site
python -m scripts.download_frontend --url https://jiffy.secondavenue.com --output playground/frontend

# Now edit the HTML, CSS, or JS files and open in browser
# Navigate to: file:///C:\Users\GCS\NWCHBSoul\web_automation_project\playground\frontend\index.html
```

### Scenario 4: Add Capture Data as Fixtures

After running the real automation on the live site:

1. Check `results/api_captures_enhanced.json` for captured network logs.
2. Extract the response bodies and status codes.
3. Add new fixture files to `playground/api_fixtures/`.
4. Restart the mock server to load the new fixtures.

Example: Extract from `results/api_captures_enhanced.json` and save as `playground/api_fixtures/search_results.json`:

```json
{
  "status": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "query": "john smith",
    "results": [
      {
        "id": 1,
        "name": "John Smith",
        "unit": "101A"
      }
    ]
  }
}
```

## Advanced: Running Multiple Scenarios in Parallel

You can run multiple mock servers on different ports to simulate different API states:

```powershell
# Terminal 1: Main server
python -m scripts.mock_api_server --port 5000 --fixtures-dir playground/api_fixtures

# Terminal 2: Error scenario server
# (Create a copy of api_fixtures with error responses)
python -m scripts.mock_api_server --port 5001 --fixtures-dir playground/api_fixtures_errors

# Terminal 3: Your automation test
python scripts/test_automation.py --api-url http://localhost:5000
```

## Integration with CI/CD

Add to your CI/CD pipeline:

```powershell
# Start mock server in background
Start-Process python -ArgumentList @("-m", "scripts.mock_api_server", "--port", "5000") -NoNewWindow

# Run tests
python -m pytest tests/test_playground.py

# Kill mock server
Stop-Process -Name python
```

## Debugging

### Check Request Log

```powershell
curl http://localhost:5000/mock-api/request-log | python -m json.tool
```

### Check Loaded Fixtures

```powershell
curl http://localhost:5000/mock-api/fixtures | python -m json.tool
```

### Add Logging to Mock Server

Edit `scripts/mock_api_server.py` to log request details:

```python
logger.info(f"Request: {method} {path}")
logger.info(f"Body: {body}")
logger.info(f"Headers: {headers}")
```

## Next Steps

1. **Download Real Frontend:** Run `scripts/download_frontend.py` to get HTML/CSS/JS from the live site.
2. **Extract Real Captures:** From `results/api_captures_enhanced.json`, create fixture files for real API responses.
3. **Run Integration Tests:** Use `tests/test_playground.py` to verify your automation works against the mock server.
4. **Iterate Safely:** Modify fixtures and frontend code to test edge cases and new features without risking the live site.

---

**Remember:** This playground is your safe sandbox. Break things here. Learn. Iterate. Only then deploy to production.
