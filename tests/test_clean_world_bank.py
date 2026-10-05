from __future__ import annotations

import json

import pandas as pd
import pytest

from src.transform.clean_world_bank import (
    build_staging_world_bank,
    clean_world_bank,
)


def make_payload(
    values: dict[str, object],
    year: int = 2019,
    country_names: dict[str, str] | None = None,
) -> list:
    """
    Build a small World Bank API-like JSON payload.

    values maps ISO-3 code -> indicator value.
    """
    country_names = country_names or {
        "PHL": "Philippines",
        "USA": "United States",
        "AFE": "Africa Eastern and Southern",
    }

    records = []

    for iso_code, value in values.items():
        records.append(
            {
                "countryiso3code": iso_code,
                "country": {
                    "value": country_names.get(
                        iso_code,
                        iso_code,
                    )
                },
                "date": str(year),
                "value": value,
            }
        )

    return [
        {
            "page": 1,
            "pages": 1,
            "total": len(records),
        },
        records,
    ]


def build_test_payloads():
    gdp = make_payload(
        {
            "PHL": "376823402239.136",
            "USA": "21380976119000",
            "AFE": "1019354194063.69",
        }
    )

    population = make_payload(
        {
            "PHL": "110804683",
            "USA": "328329953",
            "AFE": "675950189",
        }
    )

    gdp_per_capita = make_payload(
        {
            "PHL": "3400.78949767074",
            "USA": "65120.394663",
            "AFE": "1508.0315245887",
        }
    )

    return gdp, population, gdp_per_capita


def test_clean_world_bank_builds_expected_table():
    gdp, population, gdp_per_capita = build_test_payloads()

    result = clean_world_bank(
        gdp,
        population,
        gdp_per_capita,
    )

    assert result["iso_code"].tolist() == [
        "AFE",
        "PHL",
        "USA",
    ]

    assert result["wb_year"].tolist() == [
        2019,
        2019,
        2019,
    ]

    assert set(result.columns) == {
        "iso_code",
        "wb_country",
        "wb_year",
        "wb_gdp_current_usd",
        "wb_population",
        "wb_gdp_per_capita_current_usd",
    }


def test_clean_world_bank_converts_indicator_values_to_numeric():
    gdp, population, gdp_per_capita = build_test_payloads()

    result = clean_world_bank(
        gdp,
        population,
        gdp_per_capita,
    )

    assert pd.api.types.is_numeric_dtype(
        result["wb_gdp_current_usd"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["wb_population"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["wb_gdp_per_capita_current_usd"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["wb_year"]
    )


def test_clean_world_bank_preserves_missing_indicator_values():
    gdp, population, gdp_per_capita = build_test_payloads()

    gdp[1][1]["value"] = None

    result = clean_world_bank(
        gdp,
        population,
        gdp_per_capita,
    )

    usa = result[
        result["iso_code"] == "USA"
    ].iloc[0]

    assert pd.isna(
        usa["wb_gdp_current_usd"]
    )

    assert usa["wb_population"] > 0


def test_clean_world_bank_keeps_valid_three_letter_aggregate_codes():
    gdp, population, gdp_per_capita = build_test_payloads()

    result = clean_world_bank(
        gdp,
        population,
        gdp_per_capita,
    )

    # AFE is a World Bank aggregate, but it is still a valid
    # three-letter World Bank code at the staging layer.
    assert "AFE" in set(
        result["iso_code"]
    )


def test_clean_world_bank_filters_invalid_iso_codes():
    gdp, population, gdp_per_capita = build_test_payloads()

    for payload in [
        gdp,
        population,
        gdp_per_capita,
    ]:
        payload[1].append(
            {
                "countryiso3code": "",
                "country": {
                    "value": "Invalid aggregate"
                },
                "date": "2019",
                "value": 100,
            }
        )

    result = clean_world_bank(
        gdp,
        population,
        gdp_per_capita,
    )

    assert "" not in set(
        result["iso_code"]
    )

    assert result["iso_code"].notna().all()


def test_clean_world_bank_filters_other_years():
    old_gdp = make_payload(
        {"PHL": 100},
        year=2018,
    )

    old_population = make_payload(
        {"PHL": 100},
        year=2018,
    )

    old_gdp_per_capita = make_payload(
        {"PHL": 100},
        year=2018,
    )

    with pytest.raises(
        ValueError,
        match="contains no records",
    ):
        clean_world_bank(
            old_gdp,
            old_population,
            old_gdp_per_capita,
        )


def test_clean_world_bank_rejects_duplicate_iso_codes():
    gdp, population, gdp_per_capita = build_test_payloads()

    gdp[1].append(
        {
            "countryiso3code": "PHL",
            "country": {
                "value": "Philippines"
            },
            "date": "2019",
            "value": 123,
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate ISO-3 codes",
    ):
        clean_world_bank(
            gdp,
            population,
            gdp_per_capita,
        )


def test_clean_world_bank_rejects_inconsistent_country_keys():
    gdp, population, gdp_per_capita = build_test_payloads()

    population[1][0]["country"] = {
        "value": "Different Philippines Name"
    }

    with pytest.raises(
        ValueError,
        match="inconsistent country keys",
    ):
        clean_world_bank(
            gdp,
            population,
            gdp_per_capita,
        )


def test_clean_world_bank_rejects_invalid_payload_structure():
    _, population, gdp_per_capita = build_test_payloads()

    with pytest.raises(
        ValueError,
        match="Unexpected World Bank JSON response structure",
    ):
        clean_world_bank(
            {"invalid": "payload"},
            population,
            gdp_per_capita,
        )


def test_build_staging_world_bank_writes_parquet(tmp_path):
    gdp, population, gdp_per_capita = build_test_payloads()

    raw_dir = tmp_path / "world_bank"
    raw_dir.mkdir()

    files = {
        "world_bank_gdp_current_usd.json": gdp,
        "world_bank_population.json": population,
        "world_bank_gdp_per_capita.json": gdp_per_capita,
    }

    for filename, payload in files.items():
        path = raw_dir / filename

        path.write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    output_path = (
        tmp_path
        / "stg_world_bank_2019.parquet"
    )

    result = build_staging_world_bank(
        raw_dir,
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


def test_build_staging_world_bank_missing_files_raises(tmp_path):
    raw_dir = tmp_path / "world_bank"
    raw_dir.mkdir()

    output_path = (
        tmp_path
        / "stg_world_bank_2019.parquet"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Missing World Bank raw file",
    ):
        build_staging_world_bank(
            raw_dir,
            output_path,
        )