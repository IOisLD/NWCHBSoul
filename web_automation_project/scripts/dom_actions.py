# scripts/dom_actions.py

from .output_container import OutputContainer
import pandas as pd


class DOMActions:
    """Simple DOM helper used by `main.py`.

    Provides small convenience wrappers around a Playwright `page` object
    so `main.py` can call `dom.fill_input(...)` and `dom.click_button(...)`.
    """

    def __init__(self, page):
        self.page = page

    def fill_input(self, selector: str, value, clear: bool = False):
        try:
            if clear:
                self.page.fill(selector, "")
            self.page.fill(selector, str(value))
        except Exception as e:
            print(f"[DOM] fill_input error for {selector}: {e}")

    def click_button(self, selector: str):
        try:
            self.page.click(selector)
        except Exception as e:
            print(f"[DOM] click_button error for {selector}: {e}")

    def find_resident_href(self, name: str):
        """Find a resident row by name and return a matching href or None.

        Strategy:
        - Find table cells/rows containing the name (case-insensitive).
        - For the matching row, prefer an `a` tag href, or a span with an href-like attribute.
        """
        if not self.page:
            print("[DOM] page not available for find_resident_href")
            return None

        try:
            # Search for table cells containing the name text
            candidates = self.page.query_selector_all("td")
            name_lower = name.strip().lower()
            for td in candidates:
                try:
                    text = td.inner_text().strip().lower()
                except Exception:
                    text = ""
                if name_lower and name_lower in text:
                    # look for <a> inside td
                    a = td.query_selector("a")
                    if a:
                        try:
                            href = a.get_attribute("href")
                            if href:
                                return href
                        except Exception:
                            pass
                    # look for span with data-href or aria-label/href-like
                    span = td.query_selector("span")
                    if span:
                        try:
                            href = span.get_attribute("href") or span.get_attribute("data-href") or span.get_attribute("data-url")
                            if href:
                                return href
                        except Exception:
                            pass
            return None
        except Exception as e:
            print(f"[DOM] find_resident_href error: {e}")
            return None

    def describe_common_buttons(self, limit=10):
        """Return a list of common button texts and classes found on the page (for logging).

        This helps the dry-run log describe what interactive actions are available.
        """
        if not self.page:
            print("[DOM] page not available for describe_common_buttons")
            return []

        out = []
        try:
            buttons = self.page.query_selector_all("button, a")
            seen = set()
            for b in buttons[:limit]:
                try:
                    text = (b.inner_text() or "").strip()
                    cls = b.get_attribute("class") or ""
                    key = (text, cls)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append({"text": text, "class": cls})
                except Exception:
                    continue
        except Exception as e:
            print(f"[DOM] describe_common_buttons error: {e}")
        return out

    def inject_fetch_logger(self):
        """Inject JavaScript to log all POST fetch requests to window.__capturedFetches.

        This allows tracking of API calls made by the page without manually intercepting network traffic.
        Returns True if injection succeeded, False otherwise.
        """
        if not self.page:
            print("[DOM] page not available for inject_fetch_logger")
            return False

        try:
            from .utils import get_fetch_logger_script
            script = get_fetch_logger_script()
            self.page.evaluate(script)
            print("[DOM] Fetch logger injected successfully")
            return True
        except Exception as e:
            print(f"[DOM] Failed to inject fetch logger: {e}")
            return False

    def get_captured_fetches(self):
        """Retrieve all captured fetches from `window.__capturedFetches`.

        Returns a list of dictionaries. Each entry may include keys:
        - `method`: HTTP method (e.g. "POST")
        - `url`: request URL
        - `requestBody`: body sent with the request (may be stringified JSON)
        - `requestHeaders`: request headers
        - `status`: numeric HTTP response status (when available)
        - `statusText`: response status text
        - `responseBody`: response body as text (when captured)
        - `responseHeaders`: captured response headers
        - `timestamp`: request start timestamp
        - `completedAt`: request completion timestamp
        - `error`: error string if the request failed
        """
        if not self.page:
            print("[DOM] page not available for get_captured_fetches")
            return []

        try:
            fetches = self.page.evaluate("window.__capturedFetches || []")
            return fetches if isinstance(fetches, list) else []
        except Exception as e:
            print(f"[DOM] Failed to get captured fetches: {e}")
            return []


def perform_actions(excel_path, output_container: OutputContainer, dry_run=True):
    """
    Perform web DOM actions dynamically based on Excel input.
    If dry_run=True, only simulate actions and store results in output container.
    """
    df = pd.read_excel(excel_path)

    for idx, row in df.iterrows():
        # Extract matching info
        tenant_name = row.get('Tenant Name', '')
        property_addr = row.get('Property Address', '')
        receipt_amt = row.get('Receipt Amount', 0)
        status = row.get('Status', '')

        # Only process if Status is Pending
        if str(status).lower() != 'pending':
            continue

        # Simulate mapping Excel → Web DOM fields
        mapped_data = {
            "tenant_name_web": tenant_name.upper(),  # example mapping
            "property_addr_web": property_addr.upper(),
            "receipt_amt_web": receipt_amt,
            "status_web": status
        }

        if dry_run:
            print(f"[DRY-RUN] Would update: {mapped_data}")
        else:
            # Here you'd integrate actual Playwright/requests code to POST
            pass

        # Store in output container
        output_container.add(mapped_data)
