from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PROCESSED_DATA_PATH, RAW_DATA_PATH


REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the original Excel dataset."""
    return pd.read_excel(path, engine="openpyxl")


def clean_retail_data(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate the notebook cleaning flow with project-safe paths."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    cleaned = df.copy()
    cleaned = cleaned.dropna(subset=["CustomerID"])
    cleaned = cleaned[~cleaned["InvoiceNo"].astype(str).str.startswith("C")]
    cleaned = cleaned[cleaned["Quantity"] > 0]
    cleaned = cleaned[cleaned["UnitPrice"] > 0]
    cleaned["CustomerID"] = cleaned["CustomerID"].astype(int)
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"])
    cleaned["Description"] = cleaned["Description"].fillna("Unknown Product").astype(str).str.strip()
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["UnitPrice"]
    cleaned = cleaned.sort_values("InvoiceDate").reset_index(drop=True)
    return cleaned


def save_processed_data(df: pd.DataFrame, path: Path = PROCESSED_DATA_PATH) -> Path:
    """Persist the cleaned dataset to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def ensure_processed_data(force_refresh: bool = False) -> pd.DataFrame:
    """Load the cleaned dataset, building it from raw data if required."""
    if force_refresh or not PROCESSED_DATA_PATH.exists():
        cleaned = clean_retail_data(load_raw_data())
        save_processed_data(cleaned)
        return cleaned

    return pd.read_csv(PROCESSED_DATA_PATH, parse_dates=["InvoiceDate"])


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add reusable time dimensions for dashboard analysis."""
    enriched = df.copy()
    enriched["InvoiceYear"] = enriched["InvoiceDate"].dt.year
    enriched["InvoiceMonth"] = enriched["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    enriched["InvoiceMonthLabel"] = enriched["InvoiceDate"].dt.strftime("%b %Y")
    enriched["InvoiceDay"] = enriched["InvoiceDate"].dt.day
    enriched["InvoiceHour"] = enriched["InvoiceDate"].dt.hour
    enriched["InvoiceWeekday"] = enriched["InvoiceDate"].dt.day_name()
    return enriched


def load_dataset(force_refresh: bool = False) -> pd.DataFrame:
    """Return the cleaned dataset enriched with time features."""
    return add_time_features(ensure_processed_data(force_refresh=force_refresh))

