# scripts/excel_helper.py

import shutil
import os

def copy_production_excel(src_path, dest_path="web_automation_project/input_data/input.xlsx"):
    """
    Copy production Excel file into input_data for dry-run/testing.
    
    Args:
        src_path (str): Full path to production Excel file.
        dest_path (str): Path to input_data/input.xlsx
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source Excel file not found: {src_path}")
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)
    print(f"[INFO] Production Excel copied to {dest_path}")
