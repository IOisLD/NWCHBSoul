# scripts/dry_run.py

from .excel_helper import copy_production_excel
from .dom_actions import perform_actions
from .output_container import OutputContainer
from .instructions_generator import generate_instructions
import os

class DryRunController:
    def __init__(self, excel_source, dry_run=True):
        self.excel_path = os.path.join("input_data", "input.xlsx")
        self.excel_source = excel_source
        self.dry_run = dry_run
        self.output = OutputContainer()

    def prepare_input(self):
        # Copy production or test Excel into input_data
        copy_production_excel(self.excel_source, self.excel_path)

    def run(self):
        print("[INFO] Starting dry-run...")
        # Step 1: Prepare input
        self.prepare_input()
        
        # Step 2: Generate instructions
        generate_instructions(instructions=[
            "Dry-run update for tenants:",
            "- Map 'Payee' to web field using wildsearch",
            "- Match 'Property Address' ignoring extra text",
            "- Use 'Receipt Amount' as new payment",
            "- Only update if 'Status' is 'Pending'"
        ])

        # Step 3: Perform actions (simulated)
        # perform_actions should handle DOM mapping, Excel matching, and store results in output
        perform_actions(excel_path=self.excel_path, output_container=self.output, dry_run=self.dry_run)
        
        # Step 4: Save dry-run results
        self.output.save_results(os.path.join("results", "output_dry_run.xlsx"))
        print("[INFO] Dry-run completed. Results saved to results/output_dry_run.xlsx")
