from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


SNAPSHOT_YEAR = 2019

WORLD_BANK_FILES = {
    "gdp_current_usd": "world_bank_gdp_current_usd.json",
    "population": "world_bank_population.json",
    "gdp_per_capita": "world_bank_gdp_per_capita.json",
}


def _normalize_indicator(
    payload: object,
    output_column: str,
    snapshot_year: int = SNAPSHOT_YEAR,
) -> pd.DataFrame:
    """
    Normalize one raw World Bank API JSON response.

    Expected World Bank API structure:

        [
            metadata,
            records
        ]

    The returned table contains one row per valid ISO-3 code
    for the requested year.
    """
    if (
        not isinstance(payload, list)
        or len(payload) < 2
        or not isinstance(payload[1], list)
    ):
        raise ValueError(
            "Unexpected World Bank JSON response structure."
        )

    records = payload[1]
    rows = []

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                "World Bank response contains a non-object record."
            )

        country_info = record.get("country") or {}

        if not isinstance(country_info, dict):
            country_info = {}

        rows.append(
            {
                "iso_code": record.get("countryiso3code"),
                "wb_country": country_info.get("value"),
                "wb_year": record.get("date"),
                output_column: record.get("value"),
            }
        )

    indicator_df = pd.DataFrame(rows)

    if indicator_df.empty:
        raise ValueError(
            f"World Bank response contains no records for {output_column}."
        )

    indicator_df["iso_code"] = (
        indicator_df["iso_code"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )

    indicator_df["wb_country"] = (
        indicator_df["wb_country"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    indicator_df["wb_year"] = pd.to_numeric(
        indicator_df["wb_year"],
        errors="coerce",
    )

    indicator_df[output_column] = pd.to_numeric(
        indicator_df[output_column],
        errors="coerce",
    )

    # Keep valid three-letter ISO-style country codes.
    indicator_df = indicator_df[
        indicator_df["iso_code"].str.match(
            r"^[A-Z]{3}$",
            na=False,
        )
    ].copy()

    # Keep only the requested snapshot year.
    indicator_df = indicator_df[
        indicator_df["wb_year"].eq(snapshot_year)
    ].copy()

    if indicator_df.empty:
        raise ValueError(
            f"World Bank response contains no records "
            f"for {output_column} in {snapshot_year}."
        )

    duplicate_count = int(
        indicator_df["iso_code"]
        .duplicated()
        .sum()
    )

    if duplicate_count:
        raise ValueError(
            f"{output_column} contains "
            f"{duplicate_count} duplicate ISO-3 codes."
        )

    return indicator_df.reset_index(drop=True)


def clean_world_bank(
    gdp_current_usd_payload: object,
    population_payload: object,
    gdp_per_capita_payload: object,
    snapshot_year: int = SNAPSHOT_YEAR,
) -> pd.DataFrame:
    """
    Build the World Bank staging table from the three raw indicator responses.

    Output grain:

        one row = one World Bank ISO-3 code for the snapshot year

    Indicators:
    - GDP (current US$)
    - Population, total
    - GDP per capita (current US$)

    Missing source values remain missing and are not replaced with zero.
    """
    gdp = _normalize_indicator(
        gdp_current_usd_payload,
        "wb_gdp_current_usd",
        snapshot_year,
    )

    population = _normalize_indicator(
        population_payload,
        "wb_population",
        snapshot_year,
    )

    gdp_per_capita = _normalize_indicator(
        gdp_per_capita_payload,
        "wb_gdp_per_capita_current_usd",
        snapshot_year,
    )

    indicator_tables = [
        gdp,
        population,
        gdp_per_capita,
    ]

    # Build the common country-key table from all indicators.
    country_keys = pd.concat(
        [
            table[
                [
                    "iso_code",
                    "wb_country",
                    "wb_year",
                ]
            ]
            for table in indicator_tables
        ],
        ignore_index=True,
    )

    # Confirm that each ISO code maps consistently to one country name/year.
    key_conflicts = (
        country_keys
        .groupby("iso_code", dropna=False)
        .agg(
            country_names=("wb_country", "nunique"),
            years=("wb_year", "nunique"),
        )
    )

    if (
        (key_conflicts["country_names"] > 1).any()
        or (key_conflicts["years"] > 1).any()
    ):
        raise ValueError(
            "World Bank indicators contain inconsistent country keys."
        )

    country_keys = (
        country_keys
        .drop_duplicates(
            subset=["iso_code"]
        )
        .reset_index(drop=True)
    )

    world_bank = country_keys.copy()

    for table, value_column in [
        (gdp, "wb_gdp_current_usd"),
        (population, "wb_population"),
        (
            gdp_per_capita,
            "wb_gdp_per_capita_current_usd",
        ),
    ]:
        world_bank = world_bank.merge(
            table[
                [
                    "iso_code",
                    value_column,
                ]
            ],
            on="iso_code",
            how="outer",
            validate="one_to_one",
        )

    world_bank["wb_year"] = snapshot_year

    world_bank = (
        world_bank
        .sort_values("iso_code")
        .reset_index(drop=True)
    )

    return world_bank


def _read_json(path: Path) -> object:
    """Read a World Bank raw JSON file."""
    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in World Bank file: {path}"
        ) from error


def build_staging_world_bank(
    raw_dir: str | Path,
    output_path: str | Path,
    snapshot_year: int = SNAPSHOT_YEAR,
) -> pd.DataFrame:
    """
    Read the three World Bank raw indicator files,
    build the staging table, and write it as Parquet.
    """
    raw_dir = Path(raw_dir)
    output_path = Path(output_path)

    paths = {
        name: raw_dir / filename
        for name, filename in WORLD_BANK_FILES.items()
    }

    missing_files = [
        str(path)
        for path in paths.values()
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing World Bank raw file(s): "
            + ", ".join(missing_files)
        )

    gdp_payload = _read_json(
        paths["gdp_current_usd"]
    )

    population_payload = _read_json(
        paths["population"]
    )

    gdp_per_capita_payload = _read_json(
        paths["gdp_per_capita"]
    )

    staging_df = clean_world_bank(
        gdp_current_usd_payload=gdp_payload,
        population_payload=population_payload,
        gdp_per_capita_payload=gdp_per_capita_payload,
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