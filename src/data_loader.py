"""
Data Loader and Preprocessing Module for COVID-19 Data Explorer.
Handles data ingestion, missing-value imputation, reproducible cleaning,
and data validation against college assignment specifications.
"""

from pathlib import Path
from typing import Optional, Tuple
import pandas as pd


# Default location relative to repository root
DEFAULT_DATA_FILENAME = "COVID-19 Coronavirus.csv"


def resolve_data_path(custom_path: Optional[str] = None) -> Path:
    """
    Resolves dataset path robustly across local development,
    Streamlit cloud deployment, and subfolder execution.
    """
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p

    # Candidate paths
    candidate_paths = [
        Path("data") / DEFAULT_DATA_FILENAME,
        Path(__file__).resolve().parent.parent / "data" / DEFAULT_DATA_FILENAME,
        Path(__file__).resolve().parent.parent / DEFAULT_DATA_FILENAME,
        Path(DEFAULT_DATA_FILENAME),
        Path(r"D:\GEN AI") / DEFAULT_DATA_FILENAME,
    ]

    for cand in candidate_paths:
        if cand.exists():
            return cand.resolve()

    raise FileNotFoundError(
        f"Unable to locate '{DEFAULT_DATA_FILENAME}'. Searched: {[str(c) for c in candidate_paths]}"
    )


def load_raw_data(data_path: Optional[str] = None) -> pd.DataFrame:
    """Loads raw dataset without alterations."""
    resolved = resolve_data_path(data_path)
    return pd.read_csv(resolved)


def clean_covid_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Reproducibly cleans the COVID-19 dataset according to assignment requirements:
    1. Fill missing 'Other names' with 'Montenegro'
    2. Rename 'ISO 3166-1 alpha-3 CODE' to 'Iso_Code'
    3. Standardize column names (strip non-breaking spaces \xa0 for reliable querying)
       while maintaining exact underlying data.

    Returns:
        Tuple[pd.DataFrame, dict]: Cleaned dataframe and verification audit dictionary.
    """
    df = raw_df.copy()

    # Pre-cleaning audit
    initial_null_count = int(df.isnull().sum().sum())
    missing_before = df[df.isnull().any(axis=1)].copy()
    row_135_before = df.iloc[135].to_dict() if len(df) > 135 else {}

    # Requirement 8: Replace the missing value with 'Montenegro'
    df["Other names"] = df["Other names"].fillna("Montenegro")

    # Requirement 11: Rename ISO code column
    df.rename(columns={"ISO 3166-1 alpha-3 CODE": "Iso_Code"}, inplace=True)

    # Normalize column names for safe access (replace non-breaking space \xa0 and double slashes)
    rename_clean_map = {}
    for col in df.columns:
        clean_col = col.replace("\xa0", " ").replace("//", "/").strip()
        if clean_col != col:
            rename_clean_map[col] = clean_col

    if rename_clean_map:
        df.rename(columns=rename_clean_map, inplace=True)

    # Post-cleaning audit
    final_null_count = int(df.isnull().sum().sum())
    row_135_after = df.iloc[135].to_dict() if len(df) > 135 else {}

    audit_report = {
        "initial_null_count": initial_null_count,
        "final_null_count": final_null_count,
        "missing_rows_count": len(missing_before),
        "row_135_verified": row_135_after.get("Other names") == "Montenegro",
        "row_135_snapshot": row_135_after,
        "column_renames": {
            "ISO 3166-1 alpha-3 CODE": "Iso_Code",
            **rename_clean_map,
        },
        "total_records": len(df),
        "total_columns": len(df.columns),
    }

    return df, audit_report


def load_and_clean_data(data_path: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    High-level entry point returning:
    - raw_df: unmodified dataset
    - clean_df: cleaned dataset
    - audit: audit report dictionary
    """
    raw_df = load_raw_data(data_path)
    clean_df, audit = clean_covid_data(raw_df)
    return raw_df, clean_df, audit
