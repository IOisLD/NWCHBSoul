# scripts/main.py

from scripts.load_input import load_input
from scripts.utils import read_input
from scripts.output_container import OutputContainer
from scripts.browser_manager import BrowserManager
from scripts.dom_actions import DOMActions
from scripts.smart_matcher import SmartMatcher
import json
import pandas as pd
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
DRY_RUN = True
INPUT_FILE = "web_automation_project/input_data/input.xlsx"
RESULTS_FILE = "web_automation_project/results/output.xlsx"
CONFIG_FILE = "web_automation_project/config/steps_config.json"
COOKIE_FILE = "web_automation_project/config/cookies.json"

# -----------------------------
# STEP 1: Load input file and config
# -----------------------------
load_input()
df = read_input(INPUT_FILE)

with open(CONFIG_FILE) as f:
    config = json.load(f)

container = OutputContainer()
matcher = SmartMatcher(threshold=75)

# -----------------------------
# STEP 2: Start browser
# -----------------------------
with BrowserManager(headless=False, cookie_file=COOKIE_FILE) as page:
    dom = DOMActions(page)

    # Check if login page is needed
    login_cfg = config.get("login_page")
    if login_cfg and not os.path.exists(COOKIE_FILE):
        page.goto(login_cfg["url"])
        dom.fill_input(login_cfg["fields"]["username"], "<USERNAME>")
        dom.fill_input(login_cfg["fields"]["password"], "<PASSWORD>")
        dom.click_button(login_cfg["buttons"]["login"])
        print("[INFO] Logged in manually, save cookies for future runs.")

    # -----------------------------
    # STEP 3: Navigate payment update page
    # -----------------------------
    page_cfg = config["payment_update_page"]
    page.goto(page_cfg["url"])

    if page_cfg.get("dynamic_fields"):
        dom_fields = list(dom.read_inputs().keys())
    else:
        dom_fields = page_cfg["rules"]["match_columns"]

    # -----------------------------
    # STEP 4: Iterate Excel rows
    # -----------------------------
    for idx, row in df.iterrows():
        mapped = matcher.map_excel_to_dom(row.to_dict(), dom_fields)

        # Only update rows with Pending status
        status_field = page_cfg["rules"]["update_if_status"]
        if status_field in mapped and mapped[status_field] != "Pending":
            continue

        container.add_record(mapped)

        if DRY_RUN:
            print(f"[DRY RUN] Row {idx} mapped: {mapped}")
        else:
            # Fill dynamic fields
            for dom_field, value in mapped.items():
                selector = f"#{dom_field.replace(' ', '-').lower()}"
                dom.fill_input(selector, value)
            dom.click_button(page_cfg["buttons"]["submit"])

# -----------------------------
# STEP 5: Export results
# -----------------------------
pd.DataFrame(container.get_all()).to_excel(RESULTS_FILE, index=False)
print(f"[INFO] Dry run completed. Output saved to {RESULTS_FILE}")
