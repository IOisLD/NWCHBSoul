"""
Interactive Explorer — A hands-on scraper/crawler that deep-dives into page structure,
network traffic, and DOM to understand system architecture (like a new hire touring the system).

Features:
- Captures General Info (URL, title, status)
- Captures Request Headers (what we send)
- Captures Response Headers (what server sends back)
- Captures Response Body (content for schema inference)
- Introspects forms, buttons, links, and API patterns
- Exports a rich JSON structure for analysis

Usage:
    from scripts.interactive_explorer import InteractiveExplorer
    
    explorer = InteractiveExplorer(page)
    explorer.inject_network_logger()
    page.goto('https://example.com')
    report = explorer.generate_report()
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class InteractiveExplorer:
    """Deep-dive explorer that captures page structure, network traffic, and metadata."""

    def __init__(self, page, headless=True):
        """
        Args:
            page: Playwright page object
            headless: whether we're running headless (affects what we can capture)
        """
        self.page = page
        self.headless = headless
        self.captured_network = []
        self.page_metadata = {}
        self.forms = []
        self.buttons = []
        self.links = []
        self.api_endpoints = []

    def inject_network_logger(self):
        """Inject JavaScript to intercept and log all network requests/responses with full headers and bodies."""
        script = """
        (function() {
          window.__networkLog = [];
          const originalFetch = window.fetch;

          window.fetch = function(...args) {
            const url = args[0];
            const options = args[1] || {};
            const method = (options.method || 'GET').toUpperCase();
            const requestHeaders = options.headers || {};
            const requestBody = options.body || null;
            const timestamp = new Date().toISOString();

            return originalFetch.apply(this, args)
              .then(async (response) => {
                try {
                  const cloned = response.clone();
                  const responseHeaders = {};
                  
                  // Capture all response headers
                  for (let [key, value] of response.headers.entries()) {
                    responseHeaders[key] = value;
                  }
                  
                  // Capture response body (text)
                  let responseBody = null;
                  try {
                    responseBody = await cloned.text();
                  } catch (e) {
                    responseBody = null;
                  }

                  window.__networkLog.push({
                    method: method,
                    url: String(url),
                    requestHeaders: requestHeaders,
                    requestBody: requestBody,
                    status: response.status,
                    statusText: response.statusText,
                    responseHeaders: responseHeaders,
                    responseBody: responseBody,
                    timestamp: timestamp,
                    completedAt: new Date().toISOString()
                  });
                } catch (e) {
                  console.warn('network-logger error:', e);
                }
                return response;
              })
              .catch((err) => {
                window.__networkLog.push({
                  method: method,
                  url: String(url),
                  requestHeaders: requestHeaders,
                  requestBody: requestBody,
                  error: String(err),
                  timestamp: timestamp,
                  completedAt: new Date().toISOString()
                });
                throw err;
              });
          };
        })();
        """
        try:
            self.page.evaluate(script)
            return True
        except Exception as e:
            print(f"[Explorer] Failed to inject network logger: {e}")
            return False

    def get_network_log(self) -> List[Dict]:
        """Retrieve all captured network requests and responses."""
        try:
            log = self.page.evaluate("window.__networkLog || []")
            return log if isinstance(log, list) else []
        except Exception as e:
            print(f"[Explorer] Failed to retrieve network log: {e}")
            return []

    def capture_general_info(self) -> Dict:
        """Capture General Info: URL, title, status, viewport, user-agent, etc."""
        try:
            return {
                "url": self.page.url,
                "title": self.page.title(),
                "status": "loaded",
                "timestamp": datetime.utcnow().isoformat(),
                "viewport": self.page.viewport_size,
                "ua": self.page.evaluate("navigator.userAgent"),
                "language": self.page.evaluate("navigator.language")
            }
        except Exception as e:
            print(f"[Explorer] Failed to capture general info: {e}")
            return {"error": str(e)}

    def capture_response_headers(self) -> Dict:
        """
        Capture HTTP Response Headers from the main page load.
        Note: requires intercepting network; falls back to empty if not available.
        """
        try:
            # This would require response interception in real Playwright
            # For now, we capture from network logs if available
            network_log = self.get_network_log()
            if network_log and len(network_log) > 0:
                return network_log[0].get("responseHeaders", {})
            return {}
        except Exception as e:
            print(f"[Explorer] Failed to capture response headers: {e}")
            return {}

    def capture_request_headers(self) -> Dict:
        """Capture HTTP Request Headers sent to the server."""
        try:
            network_log = self.get_network_log()
            if network_log and len(network_log) > 0:
                return network_log[0].get("requestHeaders", {})
            # Fallback: common browser headers
            return {
                "User-Agent": self.page.evaluate("navigator.userAgent"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": self.page.evaluate("navigator.language")
            }
        except Exception as e:
            print(f"[Explorer] Failed to capture request headers: {e}")
            return {}

    def capture_forms(self) -> List[Dict]:
        """Introspect and capture all forms on the page."""
        forms = []
        try:
            form_elements = self.page.query_selector_all("form")
            for idx, form in enumerate(form_elements):
                try:
                    form_data = {
                        "id": form.get_attribute("id") or f"form_{idx}",
                        "action": form.get_attribute("action") or "",
                        "method": form.get_attribute("method") or "GET",
                        "enctype": form.get_attribute("enctype") or "application/x-www-form-urlencoded",
                        "fields": []
                    }
                    # Capture input fields
                    inputs = form.query_selector_all("input, textarea, select")
                    for inp in inputs:
                        try:
                            field_info = {
                                "name": inp.get_attribute("name") or "",
                                "type": inp.get_attribute("type") or "text",
                                "value": inp.get_attribute("value") or "",
                                "required": inp.get_attribute("required") is not None,
                                "placeholder": inp.get_attribute("placeholder") or ""
                            }
                            form_data["fields"].append(field_info)
                        except Exception:
                            pass
                    forms.append(form_data)
                except Exception:
                    continue
        except Exception as e:
            print(f"[Explorer] Failed to capture forms: {e}")
        return forms

    def capture_buttons(self, limit=20) -> List[Dict]:
        """Introspect and capture all interactive buttons/links."""
        buttons = []
        try:
            button_elements = self.page.query_selector_all("button, a, [role='button']")
            seen = set()
            for btn in button_elements[:limit]:
                try:
                    text = (btn.inner_text() or "").strip()[:100]
                    onclick = btn.get_attribute("onclick") or ""
                    href = btn.get_attribute("href") or ""
                    cls = btn.get_attribute("class") or ""
                    key = (text, href)
                    if key not in seen:
                        seen.add(key)
                        buttons.append({
                            "text": text,
                            "href": href,
                            "onclick": onclick,
                            "class": cls,
                            "tag": btn.evaluate("e => e.tagName", btn)
                        })
                except Exception:
                    continue
        except Exception as e:
            print(f"[Explorer] Failed to capture buttons: {e}")
        return buttons

    def capture_tables(self) -> List[Dict]:
        """Introspect and extract table structures (schema-like info)."""
        tables = []
        try:
            table_elements = self.page.query_selector_all("table")
            for idx, table in enumerate(table_elements):
                try:
                    table_info = {
                        "id": table.get_attribute("id") or f"table_{idx}",
                        "headers": [],
                        "sample_row": [],
                        "row_count": 0
                    }
                    # Extract headers
                    headers = table.query_selector_all("thead th, thead td")
                    for th in headers:
                        try:
                            table_info["headers"].append((th.inner_text() or "").strip())
                        except Exception:
                            pass
                    # Count rows
                    rows = table.query_selector_all("tbody tr")
                    table_info["row_count"] = len(rows)
                    # Sample first row
                    if len(rows) > 0:
                        cells = rows[0].query_selector_all("td")
                        for cell in cells:
                            try:
                                table_info["sample_row"].append((cell.inner_text() or "").strip())
                            except Exception:
                                pass
                    tables.append(table_info)
                except Exception:
                    continue
        except Exception as e:
            print(f"[Explorer] Failed to capture tables: {e}")
        return tables

    def capture_api_patterns(self) -> List[Dict]:
        """Extract API endpoint patterns from page HTML and network logs."""
        patterns = []
        try:
            # From network logs
            network_log = self.get_network_log()
            for entry in network_log:
                if "/api/" in entry.get("url", ""):
                    patterns.append({
                        "method": entry.get("method"),
                        "endpoint": entry.get("url"),
                        "status": entry.get("status"),
                        "type": "network_capture"
                    })
            # From HTML (script src, data attributes, etc.)
            html = self.page.content()
            api_regex = r"https?://[^\s\"']+/api/[^\s\"']+"
            api_urls = re.findall(api_regex, html)
            for url in api_urls:
                patterns.append({
                    "endpoint": url,
                    "type": "html_pattern"
                })
        except Exception as e:
            print(f"[Explorer] Failed to capture API patterns: {e}")
        return patterns

    def generate_report(self) -> Dict:
        """Generate a comprehensive exploration report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "general": self.capture_general_info(),
            "request_headers": self.capture_request_headers(),
            "response_headers": self.capture_response_headers(),
            "network_log": self.get_network_log(),
            "forms": self.capture_forms(),
            "buttons": self.capture_buttons(),
            "tables": self.capture_tables(),
            "api_patterns": self.capture_api_patterns()
        }


def explore_page(page, headless=True) -> Dict:
    """Convenience function to explore a page and return a rich report."""
    explorer = InteractiveExplorer(page, headless=headless)
    explorer.inject_network_logger()
    report = explorer.generate_report()
    return report
