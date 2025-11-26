# scripts/smart_matcher.py

from fuzzywuzzy import fuzz
from typing import List, Dict

class SmartMatcher:
    def __init__(self, threshold=80):
        self.threshold = threshold

    def find_best_match(self, value: str, candidates: List[str]):
        """Returns the best candidate match using fuzzy matching"""
        best_score = 0
        best_candidate = None
        for candidate in candidates:
            score = fuzz.partial_ratio(str(value).lower(), str(candidate).lower())
            if score > best_score and score >= self.threshold:
                best_score = score
                best_candidate = candidate
        return best_candidate

    def map_excel_to_dom(self, excel_row: Dict, dom_fields: List[str]):
        """
        Returns a dict mapping Excel values to DOM field names
        """
        mapped = {}
        for col_name, value in excel_row.items():
            match = self.find_best_match(value, dom_fields)
            if match:
                mapped[match] = value
        return mapped
