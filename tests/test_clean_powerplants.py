from __future__ import annotations

import pandas as pd
import pytest

from src.transform.clean_powerplants import (
    build_staging_powerplants,
    clean_powerplants,
)


def build_raw_powerplants() -> pd.DataFrame:
    """Small raw-like WRI fixture for transformation tests."""
    return pd.DataFrame(
        {
            "country": [" phl ", "usa", "IDN"],
            "country_long": [
                " Philippines ",
                "United States of America",
                "Indonesia",
            ],
            "name": [
                " Plant A ",
                "Plant B",
                "Plant C",
            ],
            "gppd_idnr": [
                " PHL0001 ",
                "USA0001",
                "IDN0001",
            ],
            "capacity_mw": [
                "100.5",
                "250",
                "75",
            ],
            "latitude": [
                "14.60",
                "35.00",
                "-6.20",
            ],
            "longitude": [
                "121.00",
                "-100.00",
                "106.80",
            ],
            "primary_fuel": [
                " Solar ",
                "Coal",
                "Gas",
            ],
            "other_fuel1": [
                None,
                " Oil ",
                None,
            ],
            "commissioning_year": [
                "2015",
                "1990",
                "2005",
            ],
            "generation_gwh_2019": [
                "150.0",
                "1000.5",
                None,
            ],
            "custom_source_column": [
                "keep-a",
                "keep-b",
                "keep-c",
            ],
        }
    )


def test_clean_powerplants_standardizes_core_fields():
    raw = build_raw_powerplants()

    result = clean_powerplants(raw)

    assert result["country"].tolist() == ["PHL", "USA", "IDN"]
    assert result["primary_fuel"].tolist() == ["Solar", "Coal", "Gas"]
    assert result["gppd_idnr"].tolist() == [
        "PHL0001",
        "USA0001",
        "IDN0001",
    ]

    assert pd.api.types.is_numeric_dtype(result["capacity_mw"])
    assert pd.api.types.is_numeric_dtype(result["latitude"])
    assert pd.api.types.is_numeric_dtype(result["longitude"])
    assert pd.api.types.is_numeric_dtype(result["commissioning_year"])
    assert pd.api.types.is_numeric_dtype(result["generation_gwh_2019"])


def test_clean_powerplants_preserves_source_columns():
    raw = build_raw_powerplants()

    result = clean_powerplants(raw)

    assert set(raw.columns) == set(result.columns)
    assert "custom_source_column" in result.columns


def test_clean_powerplants_does_not_mutate_input():
    raw = build_raw_powerplants()
    original = raw.copy(deep=True)

    clean_powerplants(raw)

    pd.testing.assert_frame_equal(raw, original)


def test_clean_powerplants_drops_missing_core_fields():
    raw = build_raw_powerplants()

    raw.loc[0, "country"] = None
    raw.loc[1, "gppd_idnr"] = None
    raw.loc[2, "primary_fuel"] = None

    result = clean_powerplants(raw)

    assert result.empty


def test_clean_powerplants_drops_invalid_capacity():
    raw = build_raw_powerplants()

    raw.loc[0, "capacity_mw"] = "not-a-number"
    raw.loc[1, "capacity_mw"] = "0"
    raw.loc[2, "capacity_mw"] = "-10"

    result = clean_powerplants(raw)

    assert result.empty


def test_clean_powerplants_does_not_silently_remove_duplicate_ids():
    raw = build_raw_powerplants()

    raw.loc[1, "gppd_idnr"] = raw.loc[0, "gppd_idnr"]

    result = clean_powerplants(raw)

    assert len(result) == 3
    assert result["gppd_idnr"].duplicated().sum() == 1


def test_clean_powerplants_requires_expected_columns():
    raw = build_raw_powerplants().drop(columns=["capacity_mw"])

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        clean_powerplants(raw)


def test_build_staging_powerplants_writes_parquet(tmp_path):
    raw = build_raw_powerplants()

    raw_path = tmp_path / "global_power_plant_database.csv"
    output_path = tmp_path / "stg_plants.parquet"

    raw.to_csv(
        raw_path,
        index=False,
    )

    result = build_staging_powerplants(
        raw_path,
        output_path,
    )

    assert output_path.exists()
    assert len(result) == 3

    saved = pd.read_parquet(output_path)

    pd.testing.assert_frame_equal(
        saved,
        result,
        check_dtype=False,
    )


def test_build_staging_powerplants_missing_raw_file_raises(tmp_path):
    missing_path = tmp_path / "missing.csv"
    output_path = tmp_path / "stg_plants.parquet"

    with pytest.raises(FileNotFoundError):
        build_staging_powerplants(
            missing_path,
            output_path,
        )