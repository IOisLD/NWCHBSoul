from scripts.load_input import load_input
from scripts.utils import read_input, match_value
from scripts.output_container import OutputContainer
from scripts.browser_manager import BrowserManager
from scripts.dom_actions import DOMActions

DRY_RUN = True  # Change to False for actual POSTs

# Step 1: Load input
load_input()
df = read_input("web_automation_project/input_data/input.xlsx")

# Step 2: Prepare output container
container = OutputContainer()

# Step 3: Start browser session
with BrowserManager(headless=False) as page:
    dom = DOMActions(page)
    page.goto("https://example-web-app.com/login")
    
    # Example login if required
    dom.fill_input("#username", "user")
    dom.fill_input("#password", "pass")
    dom.click_button("#login-btn")

    # Step 4: Iterate input and perform actions
    for idx, row in df.iterrows():
        # Fuzzy match property and payee
        property_match = match_value(row.get("Property"), ["Property A", "Property B"])
        payee_match = match_value(row.get("Payee"), ["John Doe", "Jane Smith"])
        
        if property_match and payee_match:
            record = {
                "property": property_match,
                "payee": payee_match,
                "receipt_amount": row.get("Receipt Amount"),
                "status": row.get("Status"),
            }
            container.add_record(record)
            
            # Dry run: just print
            if DRY_RUN:
                print(f"[DRY RUN] Would update {payee_match} @ {property_match} with {row.get('Receipt Amount')}")
            else:
                # Actual DOM actions / POST request logic here
                dom.fill_input("#receipt-amount", row.get("Receipt Amount"))
                dom.click_button("#submit-btn")

# Step 5: Optional export to results
import pandas as pd
pd.DataFrame(container.get_all()).to_excel("web_automation_project/results/output.xlsx", index=False)
print("[INFO] Dry run completed. Output saved.")
