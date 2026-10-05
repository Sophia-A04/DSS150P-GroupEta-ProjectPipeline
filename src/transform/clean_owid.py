from __future__ import annotations

from pathlib import Path

import pandas as pd


SNAPSHOT_YEAR = 2019

EXPECTED_COLUMNS = [
    "country",
    "iso_code",
    "year",
    "co2",
    "co2_per_capita",
]

FORBIDDEN_STAGING_COLUMNS = [
    "population",
    "gdp",
]


def _require_columns(df: pd.DataFrame) -> None:
    """Raise an error when required OWID source columns are missing."""
    missing = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "OWID data is missing required columns: "
            + ", ".join(missing)
        )


def clean_owid(
    df: pd.DataFrame,
    snapshot_year: int = SNAPSHOT_YEAR,
) -> pd.DataFrame:
    """
    Clean the OWID CO2 dataset for the staging layer.

    Produces one country-level snapshot for the requested year.

    Main rules:
    - preserve valid ISO-3 country records only
    - standardize ISO-3 codes
    - filter to the requested snapshot year
    - rename country to owid_country
    - remove OWID population and GDP from the integration table
    - preserve remaining OWID emissions/carbon indicators

    Duplicate ISO codes are not silently removed.
    The staging validation layer is responsible for detecting them.
    """
    _require_columns(df)

    owid = df.copy()

    # Standardize identifying fields while preserving missing values.
    owid["country"] = (
        owid["country"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    owid["iso_code"] = (
        owid["iso_code"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )

    # Convert required numeric fields safely.
    for column in ["year", "co2", "co2_per_capita"]:
        owid[column] = pd.to_numeric(
            owid[column],
            errors="coerce",
        )

    # Keep standard ISO-3 country codes only.
    owid = owid[
        owid["iso_code"].str.match(
            r"^[A-Z]{3}$",
            na=False,
        )
    ].copy()

    # Keep only the requested country-year snapshot.
    owid = owid[
        owid["year"].eq(snapshot_year)
    ].copy()

    # Rename the OWID country name so it does not conflict
    # with the WRI ISO-3 country field during integration.
    owid = owid.rename(
        columns={
            "country": "owid_country",
        }
    )

    # World Bank is the project's primary source for
    # economic and demographic indicators.
    columns_to_drop = [
        column
        for column in FORBIDDEN_STAGING_COLUMNS
        if column in owid.columns
    ]

    if columns_to_drop:
        owid = owid.drop(
            columns=columns_to_drop
        )

    # Reset index without changing country-level grain.
    owid = owid.reset_index(drop=True)

    return owid


def build_staging_owid(
    raw_path: str | Path,
    output_path: str | Path,
    snapshot_year: int = SNAPSHOT_YEAR,
) -> pd.DataFrame:
    """
    Read raw OWID data, clean it, and write the staging table as Parquet.

    Returns the staging DataFrame so the caller can immediately
    validate or inspect the result.
    """
    raw_path = Path(raw_path)
    output_path = Path(output_path)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"OWID raw dataset not found: {raw_path}"
        )

    raw_df = pd.read_csv(
        raw_path,
        low_memory=False,
    )

    staging_df = clean_owid(
        raw_df,
        snapshot_year=snapshot_year,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    staging_df.to_parquet(
        output_path,
        index=False,
    )

    return staging_df