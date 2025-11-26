from pathlib import Path
import shutil
import pandas as pd

SOURCE_FILE = Path(r"C:\Users\GCS\OneDrive - Second Avenue Group\Desktop\PaymentAR\production_file.xlsx")
PROJECT_INPUT_FILE = Path(r"web_automation_project/input_data/input.xlsx")

def convert_to_excel(src_file: Path, dest_file: Path):
    ext = src_file.suffix.lower()
    if ext in [".xlsx", ".xls"]:
        shutil.copy2(src_file, dest_file)
    elif ext == ".csv":
        df = pd.read_csv(src_file)
        df.to_excel(dest_file, index=False)
    elif ext in [".txt"]:
        df = pd.read_csv(src_file, sep="\t")
        df.to_excel(dest_file, index=False)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_input():
    PROJECT_INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    convert_to_excel(SOURCE_FILE, PROJECT_INPUT_FILE)
    print(f"[INFO] Input file ready: {PROJECT_INPUT_FILE}")

if __name__ == "__main__":
    load_input()
