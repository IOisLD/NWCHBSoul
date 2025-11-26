# scripts/main.py

import os
from pathlib import Path
import argparse

# Load dependencies
import pandas as pd  # Make sure to install: pip install pandas
from scripts.browser_manager import BrowserManager
from scripts.dom_actions import DOMActions
from scripts.load_input import load_excel
from scripts.output_container import OutputContainer
from scripts.smart_match import match_tenants
from scripts.api_replay import APIReplay
from scripts.instructions_generator import InstructionsGenerator

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
DRY_RUN = args.dry_run

# -------------------------
# Load Excel Data
# -------------------------
print("[INFO] Loading Excel input...")
input_df = load_excel(INPUT_FILE)
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
# Optional: Launch Browser for DOM Actions
# -------------------------
browser_manager = BrowserManager(headless=True)
page = browser_manager.launch()
dom = DOMActions(page)

# -------------------------
# Main Processing Loop
# -------------------------
print("[INFO] Starting main automation loop...")
for index, row in input_df.iterrows():
    # Step 1: Match tenant/property using smart matcher
    matched = match_tenants(row, api_replay)
    if not matched:
        instructions.log(f"Row {index}: No match found for {row.get('Tenant Name')} / {row.get('Property')}")
        continue

    # Step 2: Prepare record for output container
    record = {
        "property": matched.get("property"),
        "payee": matched.get("payee"),
        "receipt_amount": row.get("Receipt Amount"),
        "status": row.get("Status"),
        "timestamp": pd.Timestamp.now()
    }
    output_container.add_record(record)

    # Step 3: Generate instructions
    instructions.log(f"Row {index}: Update {record['payee']} payment to {record['receipt_amount']}")

    # Step 4: Update Web API / DOM if not dry-run
    if not DRY_RUN:
        try:
            api_replay.update_payment(record)
        except Exception as e:
            instructions.log(f"[ERROR] Failed to update row {index}: {e}")
            continue

        # Optional: Update DOM for visual testing (if needed)
        # Example: dom.fill_input("#receipt", record["receipt_amount"])
        # dom.click_button("#submit-payment")

print("[INFO] Automation loop finished.")

# -------------------------
# Save Results
# -------------------------
pd.DataFrame(output_container.get_all()).to_excel(OUTPUT_FILE, index=False)
instructions.close()
browser_manager.close()
print(f"[INFO] Results saved to {OUTPUT_FILE}")
print(f"[INFO] Instructions saved to {INSTRUCTIONS_FILE}")
