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
            highest_score = score
            best_match = candidate
    return best_match
