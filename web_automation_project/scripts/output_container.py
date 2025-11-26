# scripts/output_container.py

import pandas as pd

# Generic output container
class OutputContainer:
    def __init__(self):
        self.records = []

    def add_record(self, record: dict):
        """
        record = {
            "property": None,
            "payee": None,
            "receipt_amount": None,
            "status": None,
            "timestamp": None
        }
        """
        self.records.append(record)

    def get_all(self):
        return self.records

    def save_results(self, path):
        """
        Saves all records to Excel for dry-run or logging purposes
        """
        if not self.records:
            print("[INFO] No records to save.")
            return
        df = pd.DataFrame(self.records)
        df.to_excel(path, index=False)
        print(f"[INFO] Results saved to {path}")
