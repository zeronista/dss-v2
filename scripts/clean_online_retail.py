"""
Utility to clean and normalize the Online Retail dataset.

Steps applied:
- loads the raw CSV with explicit dtypes
- trims string columns and normalizes casing
- filters cancelled invoices (InvoiceNo starting with 'C')
- drops duplicate rows
- removes records with non-positive quantity or unit price
- coerces CustomerID into nullable integers
- fills missing descriptions with a placeholder
- computes a TotalPrice helper column
- saves the cleaned data to CSV and Parquet for fast reuse
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "online_retail.csv"
OUTPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_CSV = OUTPUT_DIR / "online_retail_cleaned.csv"
OUTPUT_PARQUET = OUTPUT_DIR / "online_retail_cleaned.parquet"


@dataclass
class CleaningSummary:
    raw_rows: int
    cleaned_rows: int
    dropped_duplicates: int
    dropped_cancelled: int
    dropped_non_positive: int
    missing_description_before: int
    missing_description_after: int
    missing_customer_id_before: int
    missing_customer_id_after: int
    unique_stock_codes: int
    processing_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["processing_timestamp"] = self.processing_timestamp
        return data


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> pd.DataFrame:
    dtype_overrides = {
        "InvoiceNo": "string",
        "StockCode": "string",
        "Description": "string",
        "Country": "string",
    }
    df = pd.read_csv(
        RAW_DATA_PATH,
        dtype=dtype_overrides,
        parse_dates=["InvoiceDate"],
    )
    return df


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningSummary]:
    raw_rows = len(df)
    missing_description_before = df["Description"].isna().sum()
    missing_customer_before = df["CustomerID"].isna().sum()

    # Normalize string columns
    for column in ("StockCode", "Description", "Country"):
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    df["StockCode"] = df["StockCode"].str.upper()

    # Fill missing description with a clear placeholder
    df["Description"] = df["Description"].fillna("UNKNOWN PRODUCT")

    # Remove cancelled invoices (InvoiceNo starting with 'C')
    cancelled_mask = df["InvoiceNo"].str.startswith("C", na=False)
    df = df.loc[~cancelled_mask].copy()
    cancelled_count = int(cancelled_mask.sum())

    # Remove non-positive quantity or unit price rows
    non_positive_mask = (df["Quantity"] <= 0) | (df["UnitPrice"] <= 0)
    non_positive_count = int(non_positive_mask.sum())
    df = df.loc[~non_positive_mask].copy()

    # Drop perfect duplicates
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Normalize CustomerID to nullable integers
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce").astype(
        "Int64"
    )

    # Create helper columns
    df["TotalPrice"] = (df["Quantity"] * df["UnitPrice"]).round(2)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["InvoiceYear"] = df["InvoiceDate"].dt.year
    df["InvoiceMonth"] = df["InvoiceDate"].dt.month

    summary = CleaningSummary(
        raw_rows=raw_rows,
        cleaned_rows=len(df),
        dropped_duplicates=duplicate_count,
        dropped_cancelled=cancelled_count,
        dropped_non_positive=non_positive_count,
        missing_description_before=int(missing_description_before),
        missing_description_after=int(df["Description"].isna().sum()),
        missing_customer_id_before=int(missing_customer_before),
        missing_customer_id_after=int(df["CustomerID"].isna().sum()),
        unique_stock_codes=df["StockCode"].nunique(),
        processing_timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
    )

    return df, summary


def save_outputs(df: pd.DataFrame, summary: CleaningSummary) -> None:
    ensure_output_dir()
    df.to_csv(OUTPUT_CSV, index=False)
    df.to_parquet(OUTPUT_PARQUET, index=False)

    summary_path = OUTPUT_DIR / "online_retail_cleaning_summary.json"
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(summary.to_dict(), fh, indent=2)


def main() -> None:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}")

    df = load_dataset()
    cleaned_df, summary = clean_dataset(df)
    save_outputs(cleaned_df, summary)

    print("Cleaning completed.")
    print(json.dumps(summary.to_dict(), indent=2))


if __name__ == "__main__":
    main()
