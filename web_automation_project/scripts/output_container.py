# scripts/output_container.py

import pandas as pd

# Generic output container
class OutputContainer:
    def __init__(self):
        self.records = []

    def add_record(self, record: dict):
        """
        Append a record. Caller should include expected fields; this helper
        normalizes metadata fields.
        """
        record.setdefault("success", False)
        record.setdefault("completed", False)
        record.setdefault("processed_timestamp", None)
        record.setdefault("api_used", None)
        record.setdefault("resident_href", None)
        self.records.append(record)

    # Backwards-compatible alias
    def add(self, record: dict):
        self.add_record(record)

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
        # Normalize timestamp column
        if "processed_timestamp" in df.columns:
            df["processed_timestamp"] = df["processed_timestamp"].apply(lambda x: x if x is None else pd.to_datetime(x))
        df.to_excel(path, index=False)
        print(f"[INFO] Results saved to {path}")
