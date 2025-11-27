from pathlib import Path
import shutil
import pandas as pd

SOURCE_FILE = Path(r"C:\Users\GCS\OneDrive - Second Avenue Group\Desktop\PaymentAR\Book1 (1).xlsx")
# Use a project-relative input path (resolved from this file) so copies and reads are reliable
PROJECT_INPUT_FILE = Path(__file__).parent.parent / "input_data" / "input.xlsx"


def convert_to_excel(src_file: Path, dest_file: Path):
    ext = src_file.suffix.lower()
    if ext in [".xlsx", ".xls"]:
        # For native Excel formats, copy the file
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


def load_excel(path):
    """Load an Excel/CSV/JSON/HTML file and return a pandas DataFrame with fallbacks.

    Behavior:
    - If project input is missing, attempt to convert/copy from `SOURCE_FILE`.
    - If file is zero-size or very small, warn and return empty DataFrame.
    - Try `openpyxl` for `.xlsx`, then CSV/TSV, JSON, HTML, then generic `read_excel` as a last resort.
    """
    p = Path(path)

    # If the project's input file doesn't exist, attempt to copy/convert the configured SOURCE_FILE
    if not p.exists():
        try:
            print(f"[INFO] Project input {p} missing — attempting to copy from SOURCE_FILE: {SOURCE_FILE}")
            PROJECT_INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            convert_to_excel(SOURCE_FILE, p)
        except Exception as e:
            print(f"[WARN] Could not prepare project input from SOURCE_FILE: {e}")

    if not p.exists():
        print(f"[WARN] Input file {p} not found — returning empty DataFrame for dry-run.")
        return pd.DataFrame([])

    # Quick check for OneDrive placeholder / empty file
    try:
        size = p.stat().st_size
        if size == 0:
            print(f"[WARN] Input file {p} appears empty (size=0). If this is a OneDrive placeholder, ensure the file is 'Always keep on this device'.")
            return pd.DataFrame([])
        if size < 500:
            print(f"[WARN] Input file {p} is very small ({size} bytes); it may be a placeholder or corrupted.")
    except Exception:
        pass

    def _read_with_fallback(file_path: Path):
        suffix = file_path.suffix.lower()

        # Read a small sample to sniff content
        sample_text = ""
        try:
            sample_bytes = file_path.open("rb").read(2048)
            try:
                sample_text = sample_bytes.decode("utf-8", errors="ignore").strip()
            except Exception:
                sample_text = ""
        except Exception:
            sample_text = ""

        # Helper to safely call read_html which returns list of DataFrames
        def try_read_html(fp):
            try:
                dfs = pd.read_html(fp)
                if isinstance(dfs, list) and len(dfs) > 0:
                    return dfs[0]
            except Exception as e:
                print(f"[WARN] read_html failed for {fp}: {e}")
            return None

        # 1) Quick path by suffix
        if suffix == ".xlsx":
            try:
                return pd.read_excel(file_path, engine="openpyxl")
            except Exception as e:
                print(f"[WARN] openpyxl failed for {file_path}: {e}")

        if suffix == ".xls":
            try:
                return pd.read_excel(file_path)
            except Exception as e:
                print(f"[WARN] read_excel (.xls) failed for {file_path}: {e}")

        if suffix == ".json":
            try:
                return pd.read_json(file_path)
            except Exception as e:
                print(f"[WARN] read_json failed for {file_path}: {e}")

        if suffix in [".htm", ".html"]:
            df = try_read_html(file_path)
            if df is not None:
                return df

        if suffix in [".csv", ".txt"]:
            # Try CSV first, then try TSV
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                print(f"[WARN] read_csv failed for {file_path}: {e}")
            try:
                return pd.read_csv(file_path, sep="\t")
            except Exception as e:
                print(f"[WARN] read_csv(tab) failed for {file_path}: {e}")

        # 2) Content sniffing for unlabeled files
        low = sample_text.lower()
        if low.startswith("{") or low.startswith("["):
            try:
                return pd.read_json(file_path)
            except Exception as e:
                print(f"[WARN] sniffed JSON but pd.read_json failed for {file_path}: {e}")

        if "<table" in low or low.startswith("<"):
            df = try_read_html(file_path)
            if df is not None:
                return df

        # if commas or tabs appear in sample, try CSV
        if "," in sample_text or "\t" in sample_text:
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                print(f"[WARN] sniffed CSV but read_csv failed for {file_path}: {e}")

        # 3) Best-effort fallbacks
        # Try openpyxl again (in case extension mismatched earlier)
        try:
            return pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            print(f"[WARN] openpyxl final attempt failed for {file_path}: {e}")

        # Try generic read_csv
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"[WARN] generic read_csv failed for {file_path}: {e}")

        # Last attempt: generic read_excel
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"[WARN] Final read_excel attempt failed for {file_path}: {e}")
            return pd.DataFrame([])

    try:
        return _read_with_fallback(p)
    except Exception as e:
        print(f"[WARN] Failed to read input file {p}: {e} — returning empty DataFrame for dry-run.")
        return pd.DataFrame([])
