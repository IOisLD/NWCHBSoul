# scripts/dom_actions.py

from scripts.output_container import OutputContainer
import pandas as pd

def perform_actions(excel_path, output_container: OutputContainer, dry_run=True):
    """
    Perform web DOM actions dynamically based on Excel input.
    If dry_run=True, only simulate actions and store results in output container.
    """
    df = pd.read_excel(excel_path)

    for idx, row in df.iterrows():
        # Extract matching info
        tenant_name = row.get('Tenant Name', '')
        property_addr = row.get('Property Address', '')
        receipt_amt = row.get('Receipt Amount', 0)
        status = row.get('Status', '')

        # Only process if Status is Pending
        if str(status).lower() != 'pending':
            continue

        # Simulate mapping Excel → Web DOM fields
        mapped_data = {
            "tenant_name_web": tenant_name.upper(),  # example mapping
            "property_addr_web": property_addr.upper(),
            "receipt_amt_web": receipt_amt,
            "status_web": status
        }

        if dry_run:
            print(f"[DRY-RUN] Would update: {mapped_data}")
        else:
            # Here you'd integrate actual Playwright/requests code to POST
            pass

        # Store in output container
        output_container.add(mapped_data)
