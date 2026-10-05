from __future__ import annotations

import pandas as pd
import pytest

from src.transform.clean_owid import (
    build_staging_owid,
    clean_owid,
)


def build_raw_owid() -> pd.DataFrame:
    """Small raw-like OWID fixture for transformation tests."""
    return pd.DataFrame(
        {
            "country": [
                " Philippines ",
                "United States",
                "Indonesia",
                "World",
                "Philippines",
            ],
            "iso_code": [
                " phl ",
                "usa",
                "IDN",
                "OWID_WRL",
                "PHL",
            ],
            "year": [
                "2019",
                2019,
                2019,
                2019,
                2018,
            ],
            "co2": [
                "150.5",
                "5000.0",
                "600.2",
                "36000.0",
                "145.0",
            ],
            "co2_per_capita": [
                "1.4",
                "15.2",
                "2.2",
                "4.7",
                "1.3",
            ],
            "population": [
                108_000_000,
                328_000_000,
                270_000_000,
                7_700_000_000,
                107_000_000,
            ],
            "gdp": [
                376_000_000_000,
                21_000_000_000_000,
                1_100_000_000_000,
                87_000_000_000_000,
                346_000_000_000,
            ],
            "coal_co2": [
                80.0,
                1000.0,
                300.0,
                15000.0,
                75.0,
            ],
            "custom_emissions_field": [
                "keep-phl",
                "keep-usa",
                "keep-idn",
                "remove-aggregate",
                "remove-old-year",
            ],
        }
    )


def test_clean_owid_standardizes_and_filters_snapshot():
    raw = build_raw_owid()

    result = clean_owid(raw)

    assert result["iso_code"].tolist() == [
        "PHL",
        "USA",
        "IDN",
    ]

    assert result["year"].tolist() == [
        2019,
        2019,
        2019,
    ]

    assert result["owid_country"].tolist() == [
        "Philippines",
        "United States",
        "Indonesia",
    ]


def test_clean_owid_keeps_only_valid_iso3_codes():
    raw = build_raw_owid()

    result = clean_owid(raw)

    assert "OWID_WRL" not in set(result["iso_code"])
    assert all(
        result["iso_code"].str.match(
            r"^[A-Z]{3}$"
        )
    )


def test_clean_owid_removes_population_and_gdp():
    raw = build_raw_owid()

    result = clean_owid(raw)

    assert "population" not in result.columns
    assert "gdp" not in result.columns


def test_clean_owid_preserves_other_emissions_columns():
    raw = build_raw_owid()

    result = clean_owid(raw)

    assert "coal_co2" in result.columns
    assert "custom_emissions_field" in result.columns


def test_clean_owid_converts_required_numeric_fields():
    raw = build_raw_owid()

    result = clean_owid(raw)

    assert pd.api.types.is_numeric_dtype(result["year"])
    assert pd.api.types.is_numeric_dtype(result["co2"])
    assert pd.api.types.is_numeric_dtype(result["co2_per_capita"])


def test_clean_owid_does_not_mutate_input():
    raw = build_raw_owid()
    original = raw.copy(deep=True)

    clean_owid(raw)

    pd.testing.assert_frame_equal(
        raw,
        original,
    )


def test_clean_owid_does_not_silently_remove_duplicate_iso_codes():
    raw = build_raw_owid()

    extra = raw.iloc[[0]].copy()
    extra["country"] = "Philippines duplicate"
    extra["iso_code"] = "PHL"
    extra["year"] = 2019

    raw = pd.concat(
        [raw, extra],
        ignore_index=True,
    )

    result = clean_owid(raw)

    assert (
        result["iso_code"]
        .duplicated()
        .sum()
        == 1
    )


def test_clean_owid_requires_expected_columns():
    raw = build_raw_owid().drop(
        columns=["co2"]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        clean_owid(raw)


def test_build_staging_owid_writes_parquet(tmp_path):
    raw = build_raw_owid()

    raw_path = tmp_path / "owid-co2-data.csv"
    output_path = tmp_path / "stg_owid_2019.parquet"

    raw.to_csv(
        raw_path,
        index=False,
    )

    result = build_staging_owid(
        raw_path,
        output_path,
    )

    assert output_path.exists()
    assert len(result) == 3

    saved = pd.read_parquet(
        output_path
    )

    pd.testing.assert_frame_equal(
        saved,
        result,
        check_dtype=False,
    )


def test_build_staging_owid_missing_raw_file_raises(tmp_path):
    missing_path = tmp_path / "missing.csv"
    output_path = tmp_path / "stg_owid_2019.parquet"

    with pytest.raises(FileNotFoundError):
        build_staging_owid(
            missing_path,
            output_path,
        )