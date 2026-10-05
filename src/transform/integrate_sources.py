from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.transform.capacity_features import (
    add_capacity_features_to_plants,
)


PLANT_REQUIRED_COLUMNS = [
    "country",
    "country_long",
    "name",
    "gppd_idnr",
    "capacity_mw",
    "primary_fuel",
]

OWID_REQUIRED_COLUMNS = [
    "iso_code",
    "owid_country",
    "year",
    "co2",
    "co2_per_capita",
]

WORLD_BANK_REQUIRED_COLUMNS = [
    "iso_code",
    "wb_country",
    "wb_year",
    "wb_gdp_current_usd",
    "wb_population",
    "wb_gdp_per_capita_current_usd",
]


def _require_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    source_name: str,
) -> None:
    """Raise an error when required integration columns are missing."""
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{source_name} is missing required columns: "
            + ", ".join(missing)
        )


def _require_unique_key(
    df: pd.DataFrame,
    key: str,
    source_name: str,
) -> None:
    """Require one source row per integration key."""
    duplicate_count = int(
        df[key]
        .duplicated()
        .sum()
    )

    if duplicate_count:
        raise ValueError(
            f"{source_name} contains "
            f"{duplicate_count} duplicate {key} values."
        )


def integrate_sources(
    plants: pd.DataFrame,
    owid: pd.DataFrame,
    world_bank: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the curated three-source plant-level dataset.

    Flow:
        WRI plants
        -> installed-capacity features
        -> OWID 2019 country indicators
        -> World Bank 2019 country indicators

    Natural grain:
        one row = one real power plant

    All country-level joins are left joins so unmatched
    countries do not remove plant records.
    """
    _require_columns(
        plants,
        PLANT_REQUIRED_COLUMNS,
        "Plant staging data",
    )

    _require_columns(
        owid,
        OWID_REQUIRED_COLUMNS,
        "OWID staging data",
    )

    _require_columns(
        world_bank,
        WORLD_BANK_REQUIRED_COLUMNS,
        "World Bank staging data",
    )

    _require_unique_key(
        owid,
        "iso_code",
        "OWID staging data",
    )

    _require_unique_key(
        world_bank,
        "iso_code",
        "World Bank staging data",
    )

    original_rows = len(plants)
    original_plant_ids = set(
        plants["gppd_idnr"]
    )

    # ---------------------------------------------------------
    # 1. Add installed-capacity features to each plant.
    # ---------------------------------------------------------
    curated = (
        add_capacity_features_to_plants(
            plants
        )
    )

    # ---------------------------------------------------------
    # 2. Merge OWID 2019 indicators.
    # ---------------------------------------------------------
    curated = curated.merge(
        owid,
        left_on="country",
        right_on="iso_code",
        how="left",
        validate="many_to_one",
        indicator="_owid_merge",
    )

    curated["owid_2019_matched"] = (
        curated["_owid_merge"]
        .eq("both")
    )

    # ---------------------------------------------------------
    # 3. Merge World Bank 2019 indicators.
    #
    # Rename the World Bank key before merging so both source
    # keys remain explicit in the curated table.
    # ---------------------------------------------------------
    world_bank_merge = (
        world_bank
        .rename(
            columns={
                "iso_code":
                    "wb_iso_code"
            }
        )
        .copy()
    )

    curated = curated.merge(
        world_bank_merge,
        left_on="country",
        right_on="wb_iso_code",
        how="left",
        validate="many_to_one",
        indicator="_wb_merge",
    )

    curated["wb_2019_matched"] = (
        curated["_wb_merge"]
        .eq("both")
    )

    # ---------------------------------------------------------
    # 4. Plant-level integrity checks.
    # ---------------------------------------------------------
    if len(curated) != original_rows:
        raise RuntimeError(
            "Three-source integration changed "
            "the number of plant rows."
        )

    if curated["gppd_idnr"].duplicated().any():
        raise RuntimeError(
            "Three-source integration introduced "
            "duplicate plant IDs."
        )

    final_plant_ids = set(
        curated["gppd_idnr"]
    )

    if final_plant_ids != original_plant_ids:
        raise RuntimeError(
            "Three-source integration changed "
            "the set of plant IDs."
        )

    # Temporary pandas merge indicators are useful while
    # constructing the table but should not be exported.
    curated = curated.drop(
        columns=[
            "_owid_merge",
            "_wb_merge",
        ],
        errors="ignore",
    )

    return curated.reset_index(drop=True)


def build_curated_dataset(
    plants_path: str | Path,
    owid_path: str | Path,
    world_bank_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:
    """
    Read the three staging datasets, integrate them,
    and write the curated plant-level dataset as Parquet.
    """
    plants_path = Path(plants_path)
    owid_path = Path(owid_path)
    world_bank_path = Path(
        world_bank_path
    )
    output_path = Path(
        output_path
    )

    input_paths = {
        "plants": plants_path,
        "owid": owid_path,
        "world_bank": world_bank_path,
    }

    missing_files = [
        str(path)
        for path in input_paths.values()
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing staging file(s): "
            + ", ".join(missing_files)
        )

    plants = pd.read_parquet(
        plants_path
    )

    owid = pd.read_parquet(
        owid_path
    )

    world_bank = pd.read_parquet(
        world_bank_path
    )

    curated = integrate_sources(
        plants=plants,
        owid=owid,
        world_bank=world_bank,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    curated.to_parquet(
        output_path,
        index=False,
    )

    return curated