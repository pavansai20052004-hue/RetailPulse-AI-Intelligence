from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "online_retail.xlsx"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_online_retail.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"

