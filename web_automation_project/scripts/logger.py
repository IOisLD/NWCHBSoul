import logging
from pathlib import Path
from datetime import datetime

LOG_FOLDER = Path(__file__).parent.parent / "logs"
LOG_FOLDER.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_FOLDER / f"dry_run_{timestamp}.log"

logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_info(message: str):
    logging.info(message)
    print(message)  # optional: also print to console

def log_warn(message: str):
    logging.warning(message)
    print(f"[WARN] {message}")

def log_error(message: str):
    logging.error(message)
    print(f"[ERROR] {message}")
