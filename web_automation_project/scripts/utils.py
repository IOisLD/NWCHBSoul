import pandas as pd
from fuzzywuzzy import fuzz

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
