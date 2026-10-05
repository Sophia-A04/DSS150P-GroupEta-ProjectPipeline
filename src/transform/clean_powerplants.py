from __future__ import annotations

from pathlib import Path

import pandas as pd


CORE_REQUIRED_COLUMNS = [
    "country",
    "gppd_idnr",
    "primary_fuel",
    "capacity_mw",
]

EXPECTED_COLUMNS = [
    "country",
    "country_long",
    "name",
    "gppd_idnr",
    "capacity_mw",
    "latitude",
    "longitude",
    "primary_fuel",
]

STRING_COLUMNS = [
    "country",
    "country_long",
    "name",
    "gppd_idnr",
    "primary_fuel",
    "other_fuel1",
    "other_fuel2",
    "other_fuel3",
    "owner",
    "source",
    "url",
    "geolocation_source",
    "wepp_id",
    "generation_data_source",
]

NUMERIC_COLUMNS = [
    "capacity_mw",
    "latitude",
    "longitude",
    "commissioning_year",
    "year_of_capacity_data",
    "generation_gwh_2013",
    "generation_gwh_2014",
    "generation_gwh_2015",
    "generation_gwh_2016",
    "generation_gwh_2017",
    "generation_gwh_2018",
    "generation_gwh_2019",
    "estimated_generation_gwh_2013",
    "estimated_generation_gwh_2014",
    "estimated_generation_gwh_2015",
    "estimated_generation_gwh_2016",
    "estimated_generation_gwh_2017",
]


def _require_columns(df: pd.DataFrame) -> None:
    """Raise an error when required WRI columns are missing."""
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]

    if missing:
        raise ValueError(
            "WRI power plant data is missing required columns: "
            + ", ".join(missing)
        )


def clean_powerplants(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw WRI Global Power Plant Database for the staging layer.

    The transformation preserves the plant-level grain:
    one row = one real power plant.

    Main rules:
    - preserve the source columns
    - standardize ISO-3 country codes
    - trim important string fields
    - convert expected numerical fields to numeric
    - remove records missing core plant fields
    - keep only plants with positive installed capacity

    Duplicate plant identifiers are not silently removed here.
    They are expected to be detected by the staging validation layer.
    """
    _require_columns(df)

    plants = df.copy()

    # Standardize relevant string columns while preserving missing values.
    for column in STRING_COLUMNS:
        if column in plants.columns:
            plants[column] = plants[column].astype("string").str.strip()
            plants[column] = plants[column].replace("", pd.NA)

    # ISO-3 country codes are standardized to uppercase.
    plants["country"] = plants["country"].str.upper()

    # Convert expected numeric fields safely.
    for column in NUMERIC_COLUMNS:
        if column in plants.columns:
            plants[column] = pd.to_numeric(
                plants[column],
                errors="coerce",
            )

    # Preserve only records containing the core fields required
    # by the plant-level analytical dataset.
    plants = plants.dropna(
        subset=CORE_REQUIRED_COLUMNS
    ).copy()

    # Installed generation capacity must be positive.
    plants = plants[
        plants["capacity_mw"] > 0
    ].copy()

    # Reset the index without changing the plant-level grain.
    plants = plants.reset_index(drop=True)

    return plants


def build_staging_powerplants(
    raw_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:
    """
    Read raw WRI data, clean it, and write the staging dataset as Parquet.

    Returns the cleaned DataFrame so that the caller can immediately
    validate or inspect the staging result.
    """
    raw_path = Path(raw_path)
    output_path = Path(output_path)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"WRI raw dataset not found: {raw_path}"
        )

    raw_df = pd.read_csv(
        raw_path,
        low_memory=False,
    )

    staging_df = clean_powerplants(raw_df)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    staging_df.to_parquet(
        output_path,
        index=False,
    )

    return staging_df