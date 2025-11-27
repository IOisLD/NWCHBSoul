# scripts/main.py

import os
from pathlib import Path
import argparse

# Load dependencies
import pandas as pd  # Make sure to install: pip install pandas
from .browser_manager import BrowserManager
from .dom_actions import DOMActions
from . import load_input
from .output_container import OutputContainer
from .smart_match import match_tenants
from .api_replay import APIReplay
from .instructions_generator import InstructionsGenerator
from .logger import log_info, log_warn, log_error

# -------------------------
# Configuration & Paths
# -------------------------
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "input_data" / "input.xlsx"
OUTPUT_FILE = BASE_DIR / "results" / "output.xlsx"
INSTRUCTIONS_FILE = BASE_DIR / "results" / "instructions.txt"

# -------------------------
# CLI Arguments
# -------------------------
parser = argparse.ArgumentParser(description="Web Automation Project")
parser.add_argument("--dry-run", action="store_true", help="Run automation without submitting POSTs")
args = parser.parse_args()
DRY_RUN = True if args.dry_run else False

# -------------------------
# Load Excel Data
# -------------------------
print("[INFO] Preparing project input (will copy/convert SOURCE_FILE if needed)...")
# Ensure the project's input file exists by invoking the helper that knows the SOURCE_FILE
try:
    load_input.load_input()
except Exception as e:
    print(f"[WARN] load_input.load_input() raised: {e}")

print("[INFO] Loading Excel input...")
input_df = load_input.load_excel(INPUT_FILE)
print(f"[INFO] Loaded {len(input_df)} rows from input.xlsx")

# -------------------------
# Initialize Output Container
# -------------------------
output_container = OutputContainer()

# -------------------------
# Initialize Instructions Generator
# -------------------------
instructions = InstructionsGenerator(INSTRUCTIONS_FILE)

# -------------------------
# Initialize API Replay (cookies/auth)
# -------------------------
api_replay = APIReplay(dry_run=DRY_RUN)

# -------------------------
# Optional: Launch Browser for DOM Actions (skip when dry-run)
# -------------------------
browser_manager = None
dom = None
if not DRY_RUN:
    browser_manager = BrowserManager(headless=True)
    page = browser_manager.launch()
    dom = DOMActions(page)
    # Inject fetch logger to capture API calls
    if dom:
        dom.inject_fetch_logger()
        log_info("[SETUP] Fetch logger injected for API tracking")

# -------------------------
# Main Processing Loop
# -------------------------
print("[INFO] Starting main automation loop...")
for index, row in input_df.iterrows():
    # Step 1: Match tenant/property using smart matcher
    matched = match_tenants(row, api_replay)
    if not matched:
        instructions.log(f"Row {index}: No match found for {row.get('Tenant Name')} / {row.get('Property')}")
        log_warn(f"Row {index}: No match found for {row.get('Tenant Name')} / {row.get('Property')}")
        continue

    # Step 2: Prepare record for output container
    # Prepare record with processing metadata
    record = {
        "property": matched.get("property"),
        "payee": matched.get("payee"),
        "receipt_amount": row.get("Receipt Amount"),
        "status": row.get("Status"),
        "processed_timestamp": pd.Timestamp.now(),
        "success": False,
        "completed": False,
        "api_used": None,
        "resident_href": None,
        "dry_run": DRY_RUN,
    }
    output_container.add_record(record)

    log_info(f"Row {index}: Prepared record for {record['payee']} — dry_run={DRY_RUN}")

    # Step 3: Generate instructions
    instructions.log(f"Row {index}: Update {record['payee']} payment to {record['receipt_amount']}")
    log_info(f"Row {index}: Update {record['payee']} payment to {record['receipt_amount']}")

    # Step 4: Update Web API / DOM if not dry-run
    # Attempt API update (skip in dry-run)
    if not DRY_RUN:
        try:
            # If DOM is available, attempt to find resident href matching the payee
            if dom:
                href = dom.find_resident_href(record.get("payee") or "")
                if href:
                    record["resident_href"] = href
                    log_info(f"Row {index}: Found resident href {href}")
                # Log common buttons on the page to inform what controls exist
                buttons = dom.describe_common_buttons()
                if buttons:
                    log_info(f"Row {index}: Common buttons found: {buttons}")

            api_replay.update_payment(record)
            record["success"] = True
            record["completed"] = True
            record["api_used"] = "api_replay.update_payment"
            record["processed_timestamp"] = pd.Timestamp.now()
            log_info(f"Row {index}: API update successful")

            # After API call, capture any POST fetches that were logged
            if dom:
                fetches = dom.get_captured_fetches()
                if fetches:
                    log_info(f"Row {index}: Captured {len(fetches)} POST fetch(es)")
                    for fetch in fetches:
                        log_info(f"  - POST {fetch.get('url')}")
                        if fetch.get('body'):
                            log_info(f"    Body: {fetch.get('body')[:200]}")  # log first 200 chars

        except Exception as e:
            instructions.log(f"[ERROR] Failed to update row {index}: {e}")
            log_error(f"Row {index}: Failed to update: {e}")
            # mark as completed but failed
            record["completed"] = True
            record["success"] = False
            continue
    else:
        # Dry-run: attempt to log what would be done and DOM info if available
        if dom:
            href = dom.find_resident_href(record.get("payee") or "")
            if href:
                record["resident_href"] = href
                log_info(f"Row {index}: (dry-run) would use resident href {href}")
            buttons = dom.describe_common_buttons()
            if buttons:
                log_info(f"Row {index}: (dry-run) page buttons: {buttons}")
        log_info(f"Row {index}: (dry-run) would call api_replay.update_payment with record")

        # Optional: Update DOM for visual testing (if needed)
        # Example: dom.fill_input("#receipt", record["receipt_amount"])
        # dom.click_button("#submit-payment")

print("[INFO] Automation loop finished.")

# -------------------------
# Save Results
# -------------------------
pd.DataFrame(output_container.get_all()).to_excel(OUTPUT_FILE, index=False)
instructions.close()
if browser_manager:
    browser_manager.close()
print(f"[INFO] Results saved to {OUTPUT_FILE}")
print(f"[INFO] Instructions saved to {INSTRUCTIONS_FILE}")
