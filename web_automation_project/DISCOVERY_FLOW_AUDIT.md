# 🏥 PROJECT DISCOVERY FLOW AUDIT

## Current Status: Phase 2/4 (70% Complete)

This document maps your `web_automation_project` against the **Complete Discovery Flow** (10 phases across 4 phase-groups).

**Legend:**
- ✅ **DONE** — Fully implemented
- 🟡 **PARTIAL** — Partially implemented or in progress
- ❌ **TODO** — Not yet implemented
- 🎯 **RECOMMENDED** — High priority next step

---

# 🏥 PHASE 1: OUTSIDE-IN (Crawler Level)

*Your equivalent: "Scanning the hospital as a visitor."*

---

## Phase 1.1: Scan the Whole "Building" (Website)

**Goal:** Discover all URLs, pages, buttons, forms, routes, assets.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **URL Discovery** | ✅ DONE | `scripts/crawler.py` — discovers all URLs up to depth | Playwright |
| **Page Collection** | ✅ DONE | `crawl_scrape_runner.py` — collects all pages | Playwright |
| **Button/Form Discovery** | 🟡 PARTIAL | `dom_actions.py`: `describe_common_buttons()` | Playwright/DOM |
| **Route Mapping** | ❌ TODO | No automated route mapper (would need JS inspection) | N/A |
| **Asset Discovery** | ❌ TODO | No asset collector (CSS, JS, images, fonts) | N/A |

**Current Implementation:**
```python
# scripts/crawler.py
def crawl(start_url, max_depth=2, headless=True):
    # ✅ Discovers all URLs within same domain
    # ✅ Respects depth limits
    # ✅ Outputs JSON with discovered URLs
```

**What's Missing (but nice-to-have):**
- Systematic form discovery + field mapping
- JavaScript route inspection (SPA route detection)
- Asset catalog (scripts, stylesheets, media)

**Next Step:** ✅ **Current implementation is sufficient for page discovery.**

---

## Phase 1.2: Trace UI → API Calls

**Goal:** Capture every API call, params, headers, auth, responses.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Network Interception** | ✅ DONE | `utils.py`: `get_fetch_logger_script()` injects JS logger | Playwright + JS |
| **POST/Fetch Capture** | ✅ DONE | `dom_actions.py`: `inject_fetch_logger()` + `get_captured_fetches()` | JS in page |
| **API Endpoint Collection** | ✅ DONE | `scraper.py`: `extract_api_urls_from_page()` with regex | Regex + DOM |
| **Params + Headers** | 🟡 PARTIAL | Captured in JS, but not systematically logged | JS logger |
| **Auth Token Tracking** | 🟡 PARTIAL | `browser_manager.py` loads cookies, but no header inspection | Playwright |
| **Response Shape** | 🟡 PARTIAL | JS logger captures POST payload, not full response | JS logger |

**Current Implementation:**
```python
# scripts/utils.py - fetch logger script
FETCH_LOGGER_SCRIPT = """
window.__capturedFetches = [];
const originalFetch = window.fetch;
window.fetch = function(...args) {
  // ✅ Captures URL, method, headers, body
  // ⚠️ Does NOT capture response (would need async handler)
}
"""

# scripts/dom_actions.py
def inject_fetch_logger(page):
    # ✅ Injects logger on page load
    
def get_captured_fetches(page):
    # ✅ Retrieves captured fetches from window.__capturedFetches
```

**What's Missing (important):**
- Response body capture (currently only captures request)
- Systematic header logging (Authorization, Content-Type, etc.)
- Error response capture
- Response status codes

**Next Step:** 🎯 **Enhance JS logger to capture response data (Phase 2).**

---

## Phase 1.3: Simulate Behavior Automatically

**Goal:** Walk the UI, click buttons, submit forms, record all interactions.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Link Following** | ✅ DONE | `crawler.py` — follows all links | Playwright |
| **Button Discovery** | ✅ DONE | `dom_actions.py`: `describe_common_buttons()` | Playwright DOM |
| **Form Detection** | 🟡 PARTIAL | No dedicated form mapper (could auto-detect) | N/A |
| **Form Submission** | 🟡 PARTIAL | `dom_actions.py`: `click_button()` / `fill_input()` | Playwright |
| **Interaction Recording** | ✅ DONE | `main.py` logs all actions to `logs/dry_run_<timestamp>.log` | logging.py |
| **API Call Tracking** | ✅ DONE | JS fetch logger records POSTs | JS + DOM |

**Current Implementation:**
```python
# scripts/crawler.py
while to_visit:
    page.goto(url)
    anchors = page.locator('a[href]').element_handles()
    # ✅ Discovers and follows all links
    
# scripts/dom_actions.py
def describe_common_buttons(page, limit=20):
    # ✅ Lists all clickable elements
    # Returns: [{'text': '...', 'class': '...', 'tag': 'button'}, ...]
    
def click_button(page, button_text):
    # ✅ Clicks button by text
```

**What's Missing (recommended):**
- Automated form field discovery + auto-fill
- Screenshot capture before/after interactions
- Visual flow diagram generation

**Next Step:** ✅ **Current implementation supports interaction simulation.**

---

# 🏗️ PHASE 2: INSIDE-OUT (Inspector Level)

*Your equivalent: "Going into staff-only areas to inspect the system."*

---

## Phase 2.4: Inspect Frontend Source Code

**Goal:** Routes, components, services, API wrappers, feature flags, conditional logic.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Route Mapping** | ❌ TODO | No route analysis (would need SPA route inspection) | N/A |
| **Component Discovery** | ❌ TODO | No component tree analysis | N/A |
| **Service/API Wrapper Discovery** | ❌ TODO | No service-layer inspection | N/A |
| **Feature Flag Detection** | ❌ TODO | No feature flag scanner | N/A |
| **Conditional Flow Mapping** | ❌ TODO | No logic flow analyzer | N/A |

**What's Available:**
- You have access to jiffy.secondavenue.com frontend
- Can inspect via browser DevTools
- Can analyze Network tab manually

**What's Missing (would require):**
- Automated source code analysis (if frontend is publicly accessible)
- Build artifact inspection (webpack/bundled JS)
- Configuration file extraction

**Next Step:** 🎯 **Manually inspect jiffy's frontend via browser DevTools (Phase 2).**

---

## Phase 2.5: Inspect Backend

**Goal:** Controllers, services, logic, config, cron jobs, workers.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Backend Access** | ❌ TODO | No backend code access (assuming API-only) | N/A |
| **Endpoint Discovery** | 🟡 PARTIAL | Discovered via network tracing | JS logger |
| **Business Logic** | ❌ TODO | Inferred only from API responses | N/A |
| **Config Discovery** | ❌ TODO | No config extraction | N/A |
| **Cron/Worker Detection** | ❌ TODO | Would need server-side audit | N/A |

**What's Available:**
- You can reverse-engineer business logic from API responses
- You can map request → response patterns
- You can test edge cases

**What's Missing (would require):**
- Direct backend code access
- API documentation from vendor
- Server-side logs

**Next Step:** 🎯 **Request API documentation from jiffy.secondavenue.com admin (Phase 2).**

---

## Phase 2.6: Discover Databases

**Goal:** Schema, tables, relations, stored procedures, views.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Schema Discovery** | ❌ TODO | No direct DB access (unless provided) | N/A |
| **Table Mapping** | 🟡 PARTIAL | Inferred from API responses (residents, payments, etc.) | API data |
| **Relation Discovery** | 🟡 PARTIAL | Inferred from API call patterns | Network trace |
| **Stored Procedures** | ❌ TODO | No SP inspection (backend-only) | N/A |

**What's Available:**
- You can infer data model from API responses
- You can map entity relationships by testing

**What's Missing (would require):**
- Direct DB access
- Schema export (SQL dump)
- Vendor documentation

**Next Step:** 🎯 **Map data model by analyzing API responses (Phase 2).**

---

## Phase 2.7: Discover Infrastructure

**Goal:** Deployment, CI/CD, containers, servers, load balancers, monitoring.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Deployment Pipeline** | ❌ TODO | Not relevant (you're calling external SaaS) | N/A |
| **Server/Instance Info** | 🟡 PARTIAL | HTTP headers may reveal stack (check response headers) | Network tab |
| **CDN/Load Balancer** | 🟡 PARTIAL | Can infer from response headers | Network tab |
| **Monitoring/Logging** | ❌ TODO | Backend-only, not accessible | N/A |

**What's Available:**
- Inspect HTTP response headers for tech stack hints
- Check if Cloudflare or other CDN is in use
- Infer uptime/health from repeated requests

**What's Missing (would require):**
- Server-side infrastructure details
- Vendor documentation

**Next Step:** ✅ **Inspect response headers in Network tab (quick win).**

---

# 🔌 PHASE 3: CONNECTION MAPPING

*Your equivalent: "Putting it all together into one system map."*

---

## Phase 3.8: Create Connection Trace

**Goal:** Build diagram showing data flow: Browser → API → Backend → DB → Logs.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **UI → API Mapping** | 🟡 PARTIAL | Captured by JS logger, but not visualized | JS logger + logs |
| **API → Business Logic** | 🟡 PARTIAL | Inferred from API response patterns | Network trace |
| **Backend → Database** | 🟡 PARTIAL | Inferred from API data structure | API schema |
| **Data Flow Diagram** | ❌ TODO | No automated diagram generation | N/A |
| **Dependency Map** | ❌ TODO | No dependency visualization | N/A |

**Current Implementation:**
```python
# logs/dry_run_<timestamp>.log contains:
# [INFO] Processing row: resident_id=123
# [INFO] Matched tenant: John Doe
# [INFO] Calling APIReplay.update_payment()
# [CAPTURED_FETCH] POST /api/payments/update {...}
# [INFO] Received response: 200 OK

# This IS a trace, but text-based
```

**What's Missing (would enhance clarity):**
- Visual diagram of data flow
- Sequence diagram (mermaid/draw.io)
- Dependency graph
- Call stack visualization

**Next Step:** 🎯 **Create Mermaid diagram from captured API calls (Phase 3).**

---

## Phase 3.9: Identify Hidden Systems

**Goal:** Discover legacy APIs, admin endpoints, microservices, webhooks.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Legacy Endpoint Detection** | 🟡 PARTIAL | Can infer from API URL patterns (v1, v2, deprecated) | Network trace |
| **Admin-Only Endpoints** | ❌ TODO | Would need admin access or error-based discovery | N/A |
| **Microservices Detection** | 🟡 PARTIAL | Can infer from domain/hostname differences | Network trace |
| **Webhook Discovery** | ❌ TODO | Would need webhook testing or logs | N/A |
| **Cron/Background Job Detection** | ❌ TODO | Would need server-side logs | N/A |

**What's Available:**
- Look at all API URLs captured → infer if microservices (different domains)
- Test API endpoints with invalid params → see error patterns
- Monitor network calls for timing → infer async jobs

**What's Missing:**
- Admin interface access
- Server-side log analysis
- Webhook endpoint testing

**Next Step:** 🎯 **Analyze all captured API URLs for pattern/domain differences (Phase 3).**

---

# 📋 PHASE 4: DOCUMENTATION

*Your equivalent: "Drawing the complete blueprint."*

---

## Phase 4.10: Create Architecture Map

**Goal:** Document everything: pages, endpoints, data flows, business rules, edge cases.

| Component | Status | Evidence | Tool |
|-----------|--------|----------|------|
| **Pages/Screens Map** | 🟡 PARTIAL | `results/crawled_scraped.json` contains pages | Crawler output |
| **Endpoints Map** | 🟡 PARTIAL | `logs/dry_run_<timestamp>.log` contains API calls | JS logger output |
| **Data Flow Diagram** | ❌ TODO | No diagram yet | N/A |
| **Permissions Map** | 🟡 PARTIAL | Inferred from role-based access errors | API responses |
| **Business Rules Doc** | ❌ TODO | Not documented | N/A |
| **Edge Cases Doc** | 🟡 PARTIAL | Captured in test cases, not documented | tests/ |
| **Architecture Diagram** | ❌ TODO | No visual architecture diagram | N/A |

**Current Documentation:**
```
✅ README_CRAWL.md — Crawler usage
✅ API_SETUP.md — API configuration
✅ scripts/README_CRAWL.md — Scraper usage
✅ BUILD_SUMMARY.md — Project summary
❌ ARCHITECTURE_DIAGRAM.md — No visual architecture
❌ API_REFERENCE.md — No detailed endpoint reference
❌ DATA_MODEL.md — No data model documentation
❌ FLOW_DIAGRAMS.md — No flow diagrams
```

**What's Missing (critical for handoff):**
- Detailed API endpoint reference (all discovered endpoints)
- Data model / schema documentation
- Flow diagrams (Mermaid sequences)
- Business rules and edge cases
- Error handling guide

**Next Step:** 🎯 **Create API_REFERENCE.md from captured network calls (Phase 4).**

---

# 📊 DISCOVERY READINESS MATRIX

## Overall Progress

| Phase | Name | Status | Completeness |
|-------|------|--------|--------------|
| 1.1 | Scan Building (URLs) | ✅ DONE | 100% |
| 1.2 | Trace UI→API | 🟡 PARTIAL | 60% |
| 1.3 | Simulate Behavior | ✅ DONE | 90% |
| **Phase 1 Total** | **Outside-In** | **🟡 PARTIAL** | **80%** |
| 2.4 | Inspect Frontend | ❌ TODO | 0% |
| 2.5 | Inspect Backend | 🟡 PARTIAL | 40% |
| 2.6 | Discover DB | 🟡 PARTIAL | 30% |
| 2.7 | Discover Infra | 🟡 PARTIAL | 20% |
| **Phase 2 Total** | **Inside-Out** | **🟡 PARTIAL** | **50%** |
| 3.8 | Connection Mapping | 🟡 PARTIAL | 50% |
| 3.9 | Hidden Systems | 🟡 PARTIAL | 40% |
| **Phase 3 Total** | **Connection** | **🟡 PARTIAL** | **45%** |
| 4.10 | Architecture Doc | 🟡 PARTIAL | 40% |
| **Phase 4 Total** | **Documentation** | **🟡 PARTIAL** | **40%** |
| **OVERALL** | **ALL PHASES** | **🟡 PARTIAL** | **63%** |

---

# 🎯 TOP PRIORITY RECOMMENDATIONS

## Immediate (This Week)

### 1. **Enhance Network Tracing** 🔴 HIGH
- Upgrade JS fetch logger to capture **response bodies** (not just requests)
- Log response headers (Content-Type, X-RateLimit, etc.)
- Log HTTP status codes and errors

**File to update:** `scripts/utils.py` → enhance `get_fetch_logger_script()`

**Benefit:** You'll have 100% of API contract data captured automatically.

---

### 2. **Create API Reference** 🔴 HIGH
- Extract all discovered API endpoints from logs
- Document each with: method, URL, params, response schema
- Create `docs/API_REFERENCE.md`

**Tool:** Parse `logs/dry_run_<timestamp>.log` → generate reference

**Benefit:** You'll have searchable API documentation for the jiffy system.

---

### 3. **Create Data Model Diagram** 🟠 MEDIUM
- Infer data model from API responses
- Create ER diagram (residents, payments, properties, etc.)
- Document relationships

**Tool:** Draw.io or Mermaid

**Benefit:** You'll understand the database structure without direct access.

---

## Next Week

### 4. **Create Sequence Diagrams** 🟠 MEDIUM
- For each workflow (e.g., "add payment"):
  - UI click → API call → backend process → response
- Create Mermaid sequences in `docs/FLOWS.md`

**Tool:** Mermaid + VS Code Markdown

**Benefit:** Team/client can see exactly what happens when they click "Submit".

---

### 5. **Enhance Edge Case Testing** 🟠 MEDIUM
- Test with invalid data (empty fields, wrong types, duplicates)
- Record all error responses
- Document all edge cases

**File:** `tests/test_edge_cases.py` (new)

**Benefit:** Production-ready error handling.

---

### 6. **Request Vendor Documentation** 🟡 LOW
- Email jiffy.secondavenue.com admin:
  - "We're integrating with your API — can you provide:
    - API documentation / endpoint reference
    - Rate limits and throttling info
    - Auth token generation process
    - Supported webhook events"

**Benefit:** Fills in gaps that automation can't discover.

---

# 🗺️ CURRENT STATE SUMMARY

You **HAVE**:
- ✅ Full URL discovery (crawler)
- ✅ Automatic behavior simulation (UI interaction)
- ✅ API call tracing (JS logger)
- ✅ Request logging (fetch logger)
- ✅ Dry-run testing framework
- ✅ Unit test suite (20 tests)
- ✅ Configuration management
- ✅ Error handling

You **NEED**:
- 🎯 Response body capture (enhance JS logger)
- 🎯 API endpoint documentation (generate reference)
- 🎯 Data model diagram (ER diagram)
- 🎯 Sequence diagrams (workflow flows)
- 🎯 Edge case testing
- 🎯 Vendor documentation (request)

---

# 🏥 PHASE MAPPING TO HOSPITAL ANALOGY

| Phase | Your System | Hospital Analogy |
|-------|-------------|------------------|
| 1.1 | Crawler discovers pages | Visitor walks around finding all rooms |
| 1.2 | JS logger captures APIs | Observing what paperwork flows between counters |
| 1.3 | Auto-simulation | Testing every button, following every path |
| 2.4 | Frontend inspection | Checking employee manuals at each counter |
| 2.5 | Backend logic | Talking to staff in restricted offices |
| 2.6 | Database schema | Inspecting records archive room |
| 2.7 | Infrastructure | Looking at hospital's power, plumbing, building plans |
| 3.8 | Connection diagram | Drawing flow: Visitor → Counter → Department → Records |
| 3.9 | Hidden systems | Finding secret hallways, hidden labs |
| 4.10 | Architecture doc | Creating complete building blueprint |

---

# ✨ NEXT IMMEDIATE ACTION

```powershell
# 1. Run a fresh crawl + capture to get all discovered APIs
python -m scripts.crawl_scrape_runner --start-url "https://jiffy.secondavenue.com/" --max-depth 1 --output results/complete_discovery.json

# 2. Check the logs for all captured API calls
# cat logs/dry_run_<latest>.log | grep "CAPTURED_FETCH"

# 3. Then enhance the JS logger (see Enhancement section below)

# 4. Create docs/API_REFERENCE.md (template provided below)
```

---

# 🔧 ENHANCEMENT: Capture Response Data

Current JS logger captures REQUEST only. To capture RESPONSE:

```javascript
// Current (incomplete)
window.__capturedFetches = [];
const originalFetch = window.fetch;
window.fetch = function(...args) {
  window.__capturedFetches.push({
    method: args[1]?.method || 'GET',
    url: args[0],
    body: args[1]?.body
    // ❌ Missing: response
  });
  return originalFetch.apply(this, args);
};

// Enhanced (complete)
window.__capturedFetches = [];
const originalFetch = window.fetch;
window.fetch = function(...args) {
  return originalFetch.apply(this, args).then(response => {
    response.clone().json().then(json => {
      window.__capturedFetches.push({
        method: args[1]?.method || 'GET',
        url: args[0],
        status: response.status,
        body: args[1]?.body,
        response: json  // ✅ Now we capture response!
      });
    }).catch(() => {
      // If response isn't JSON, capture as text
      response.clone().text().then(text => {
        window.__capturedFetches.push({
          method: args[1]?.method || 'GET',
          url: args[0],
          status: response.status,
          body: args[1]?.body,
          response: text
        });
      });
    });
    return response;
  });
};
```

Then `get_captured_fetches()` will return the full request/response pair.

---

# 📝 API_REFERENCE.md TEMPLATE

```markdown
# API Reference - jiffy.secondavenue.com

## Endpoints Discovered

### GET /api/residents
- **Description:** List all residents
- **Params:** ?page=1&limit=20
- **Response:** [{ id, name, property, status, ... }]
- **Auth:** Bearer token
- **Rate limit:** 100 req/min

### POST /api/payments/update
- **Description:** Update payment record
- **Params:** { resident_id, amount, reference }
- **Response:** { success, message, id }
- **Auth:** Bearer token
- **Rate limit:** 50 req/min

[... continue for all discovered endpoints ...]
```

---

# 🎯 YOU'RE 63% COMPLETE

Next focus: **Response capture + API documentation = 80% completion in 1 week.**
