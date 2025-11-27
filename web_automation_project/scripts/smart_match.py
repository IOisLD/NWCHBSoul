"""Simple smart matching helpers used by `main.py`.

This module provides a minimal `match_tenants` function returning a
`{'property': ..., 'payee': ...}` dict so the rest of the pipeline can
proceed. It also provides a light-weight fuzzy matching fallback when
`fuzzywuzzy` is not installed.
"""

from typing import Dict, List, Optional

try:
    from fuzzywuzzy import fuzz

    def _partial_ratio(a: str, b: str) -> int:
        return fuzz.partial_ratio(a, b)
except Exception:
    # Fallback implementation using difflib when fuzzywuzzy is not available
    import difflib

    def _partial_ratio(a: str, b: str) -> int:
        a, b = str(a).lower(), str(b).lower()
        # Use simple sequence matcher ratio as an approximation
        return int(difflib.SequenceMatcher(None, a, b).ratio() * 100)


def match_tenants(row: Dict, api_replay=None) -> Optional[Dict]:
    """Return a minimal match dictionary for a given input `row`.

    This is a pragmatic placeholder: it extracts the most likely tenant/payee
    and property fields from the Excel row and returns them. If nothing is
    found, returns `None`.
    """
    # Try common column names
    payee = row.get("Tenant Name") or row.get("Payee") or row.get("Tenant")
    prop = row.get("Property") or row.get("Property Address") or row.get("Property Address")

    if not payee and not prop:
        return None

    return {"property": prop, "payee": payee}
