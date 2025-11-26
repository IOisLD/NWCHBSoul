# scripts/main.py

from scripts.load_input import load_input
from scripts.utils import read_input
from scripts.output_container import OutputContainer
from scripts.browser_manager import BrowserManager
from scripts.dom_actions import DOMActions
from scripts.smart_matcher import SmartMatcher
import pandas as pd

# -----------------------------
# CONFIGURATION
# -----------------------------
DRY_RUN = True  # Set to False for actual POST / web updates
INPUT_FILE = "web_automation_project/input_data/input.xlsx"
RESULTS_FILE = "web_automation_project/results/output.xlsx"

# -----------------------------
# STEP 1: Load input file
# -----------------------------
load_input()
df = read_input(INPUT_FILE)

# -----------------------------
# STEP 2: Prepare output container
# -----------------------------
container = OutputContainer()

# -----------------------------
# STEP 3: Initialize SmartMatcher
# -----------------------------
matcher = SmartMatcher(threshold=75)

# Example DOM field names (this can later be dynamic/read from config)
dom_fields = ["Property Address", "Tenant Name", "Receipt Amount", "Status"]

# -----------------------------
# STEP 4: Start browser session
# -----------------------------
with BrowserManager(headless=False) as page:
    dom = DOMActions(page)
    page.goto("https://example-web-app.com/login")

    # Example login (update selectors as needed)
    dom.fill_input("#username", "user")
    dom.fill_input("#password", "pass")
    dom.click_button("#login-btn")

    # -----------------------------
    # STEP 5: Iterate input and map to DOM dynamically
    # -----------------------------
    for idx, row in df.iterrows():
        # Smart mapping Excel row → DOM
        mapped = matcher.map_excel_to_dom(row.to_dict(), dom_fields)

        if not mapped:
            print(f"[WARN] Row {idx} could not be mapped to DOM fields. Skipping.")
            continue

        # Add to output container
        container.add_record(mapped)

        # -----------------------------
        # STEP 6: Dry run or actual update
        # -----------------------------
        if DRY_RUN:
            print(f"[DRY RUN] Row {idx} mapped: {mapped}")
        else:
            # Fill inputs dynamically
            for dom_field, value in mapped.items():
                # Transform field names to safe selectors
                selector = f"#{dom_field.replace(' ', '-').lower()}"
                dom.fill_input(selector, value)
            dom.click_button("#submit-btn")

# -----------------------------
# STEP 7: Export results (dry run or after execution)
# -----------------------------
pd.DataFrame(container.get_all()).to_excel(RESULTS_FILE, index=False)
print(f"[INFO] Dry run completed. Output saved to {RESULTS_FILE}")
