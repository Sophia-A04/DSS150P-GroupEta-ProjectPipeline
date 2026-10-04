from pathlib import Path

# Project root (assumes src/extract/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOGS_DIR = PROJECT_ROOT / "logs"