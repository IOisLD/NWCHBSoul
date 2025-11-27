# Testing Playground — Quick Start Card

## 🎯 The Big Picture

You now have a **"virtual hologram"** of the Jiffy website running locally. It's a sandbox where you can:
- Test automation safely (no impact to live site)
- Experiment with UI and data changes
- Debug issues in isolation
- Learn how the system works

## 🚀 Launch in 2 Steps

### Step 1: Start the Mock API Server

```powershell
cd c:\Users\GCS\NWCHBSoul\web_automation_project
.\playground\start_playground.ps1
```

You'll see:
```
Starting Mock API Server on port 5000...
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: login
[2025-11-27 14:30:00] MockAPI - INFO - Loaded fixture: api_residents
...
 * Running on http://127.0.0.1:5000
```

**Server is ready!** Keep this terminal open.

### Step 2: Use It

**In another terminal**, test the API:

```powershell
# Check server health
curl http://localhost:5000/mock-api/health

# Log in
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@jiffy.local","password":"test"}'

# Get residents
curl http://localhost:5000/api/residents

# View all requests made to the server
curl http://localhost:5000/mock-api/request-log
```

## 📋 What You Have

| Component | Location | Purpose |
|-----------|----------|---------|
| **Mock API Server** | `scripts/mock_api_server.py` | Flask app that serves mock responses |
| **Sample Fixtures** | `playground/api_fixtures/` | JSON files (login, residents, payments) |
| **Frontend** | `playground/frontend/` | Downloaded HTML/CSS/JS (run download script to populate) |
| **Tests** | `tests/test_playground.py` | 20+ integration tests |
| **Docs** | `docs/TESTING_PLAYGROUND_GUIDE.md` | Comprehensive guide |

## 🧪 Run a Test

```powershell
# Run all playground tests
python -m pytest tests/test_playground.py -v

# Expected output:
# test_server_health PASSED
# test_get_residents_list PASSED
# test_login_success PASSED
# ...
# 16 passed in 0.45s
```

## 🎮 Common Tasks

### Test Your Automation Against Local Server

```python
# scripts/my_automation.py
import requests

BASE_URL = 'http://localhost:5000'  # ← Use local, not live

# Login
response = requests.post(f'{BASE_URL}/login', json={
    'email': 'admin@jiffy.local',
    'password': 'test'
})
print(f"✓ Logged in as {response.json()['user']['name']}")

# Get residents
response = requests.get(f'{BASE_URL}/api/residents')
residents = response.json()['residents']
print(f"✓ Found {len(residents)} residents")

# Process payment
response = requests.put(f'{BASE_URL}/api/residents/1/payment', json={'amount': 500})
print(f"✓ Payment: {response.json()['transaction_id']}")
```

**Run it:**
```powershell
python scripts/my_automation.py
```

### Test Error Scenarios

Edit `playground/api_fixtures/api_residents.json` to simulate an error:

```json
{
  "status": 500,
  "headers": {"Content-Type": "application/json"},
  "body": {
    "success": false,
    "error": "Database error"
  }
}
```

Restart the server and your code will get the error response — verify it's handled correctly!

### Download Real Frontend

```powershell
python -m scripts.download_frontend --url https://jiffy.secondavenue.com --output playground/frontend
```

Then edit the HTML/CSS locally and test in your browser.

## 📊 Monitor Requests

The mock server logs every request. View them:

```powershell
curl http://localhost:5000/mock-api/request-log | python -m json.tool

# See all requests in the last session
# Useful for debugging and understanding API patterns
```

## 🔧 Add New Fixtures

Create a new JSON file in `playground/api_fixtures/`:

**File:** `playground/api_fixtures/search_results.json`
```json
{
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": {
    "query": "john",
    "results": [
      {"id": 1, "name": "John Smith"},
      {"id": 5, "name": "John Doe"}
    ]
  }
}
```

Restart the server. Now requests to `/search-results` will return this mock data.

## 📚 Learn More

- **Full Guide:** `docs/TESTING_PLAYGROUND_GUIDE.md`
- **Playground README:** `playground/README_PLAYGROUND.md`
- **Test Examples:** `tests/test_playground.py`

## 🛑 Stop the Server

```powershell
# In the terminal running the server, press Ctrl+C
```

## ✅ Checklist: Everything Works?

- [ ] Server starts without errors
- [ ] `curl http://localhost:5000/mock-api/health` returns 200
- [ ] Tests pass: `python -m pytest tests/test_playground.py -v`
- [ ] You can make requests and see responses
- [ ] Request log shows your requests

---

## 🎓 Why This Matters

This playground embodies **Safe Exploration & Experimentation:**

1. **Safe:** Can't break the live site
2. **Interactive:** Full API responses, forms, buttons captured
3. **Experimentation:** Modify data, UI, error scenarios
4. **Real-World:** Uses actual captured data from the live site
5. **Hands-On Learning:** Understand the system by playing with it

Use it to build confidence in your automation. Only when you're ready, point it at the live site.

---

**Happy experimenting!** 🚀
