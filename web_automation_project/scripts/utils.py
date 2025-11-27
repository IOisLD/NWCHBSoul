import pandas as pd
from fuzzywuzzy import fuzz

# JavaScript injection for browser automation / testing

FETCH_LOGGER_SCRIPT = """
(function () {
  const origFetch = window.fetch;
  window.__capturedFetches = [];

  window.fetch = function (...args) {
    const url = args[0];
    const options = args[1] || {};
    const method = (options.method || "GET").toUpperCase();

    if (method === "POST") {
      const logEntry = {
        method: method,
        url: url,
        body: options.body || null,
        headers: options.headers || {},
        timestamp: new Date().toISOString()
      };
      window.__capturedFetches.push(logEntry);
      console.log(
        "%cPOST FETCH: %s",
        "color: red; font-weight:bold;",
        url,
        options
      );
    }

    return origFetch.apply(this, args);
  };
})();
"""


def get_fetch_logger_script():
    """Return the JavaScript code that logs POST fetches to window.__capturedFetches."""
    return FETCH_LOGGER_SCRIPT


def read_input(file_path):
    df = pd.read_excel(file_path)
    return df

def match_value(value, candidates, threshold=80):
    """
    Returns the best match from candidates using fuzzy ratio
    """
    best_match = None
    highest_score = 0
    for candidate in candidates:
        score = fuzz.partial_ratio(str(value).lower(), str(candidate).lower())
        if score > highest_score and score >= threshold:
            FETCH_LOGGER_SCRIPT = """
            (function () {
              const origFetch = window.fetch;
              window.__capturedFetches = [];

              window.fetch = function (...args) {
                const url = args[0];
                const options = args[1] || {};
                const method = (options.method || "GET").toUpperCase();
                const startTs = new Date().toISOString();

                try {
                  const result = origFetch.apply(this, args);

                  // Capture response info when the request has a body or is a modifying method.
                  if (method === "POST" || method === "PUT" || method === "PATCH" || method === "DELETE" || options.body) {
                    result.then(async function (response) {
                      try {
                        const cloned = response.clone();
                        let bodyText = null;
                        try {
                          bodyText = await cloned.text();
                        } catch (e) {
                          bodyText = null;
                        }

                        const headers = {};
                        try {
                          response.headers.forEach((v, k) => { headers[k] = v; });
                        } catch (e) {}

                        window.__capturedFetches.push({
                          method: method,
                          url: String(url),
                          requestBody: options.body || null,
                          requestHeaders: options.headers || {},
                          status: response.status,
                          statusText: response.statusText,
                          responseBody: bodyText,
                          responseHeaders: headers,
                          timestamp: startTs,
                          completedAt: new Date().toISOString()
                        });
                      } catch (e) {
                        console.warn('fetch-logger: failed to capture response', e);
                      }
                      return response;
                    }).catch(function (err) {
                      window.__capturedFetches.push({
                        method: method,
                        url: String(url),
                        requestBody: options.body || null,
                        requestHeaders: options.headers || {},
                        error: String(err),
                        timestamp: startTs,
                        completedAt: new Date().toISOString()
                      });
                      throw err;
                    });
                  }

                  return result;
                } catch (e) {
                  return origFetch.apply(this, args);
                }
              };
            })();
            """
