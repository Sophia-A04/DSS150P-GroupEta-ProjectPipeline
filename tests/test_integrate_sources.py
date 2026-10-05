from __future__ import annotations

import pandas as pd
import pytest

from src.transform.integrate_sources import (
    build_curated_dataset,
    integrate_sources,
)


def build_plants() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "country": [
                "PHL",
                "PHL",
                "USA",
                "ZZZ",
            ],
            "country_long": [
                "Philippines",
                "Philippines",
                "United States",
                "Unmatched Country",
            ],
            "name": [
                "PHL Coal",
                "PHL Hydro",
                "USA Gas",
                "ZZZ Solar",
            ],
            "gppd_idnr": [
                "PHL001",
                "PHL002",
                "USA001",
                "ZZZ001",
            ],
            "capacity_mw": [
                100.0,
                300.0,
                500.0,
                50.0,
            ],
            "primary_fuel": [
                "Coal",
                "Hydro",
                "Gas",
                "Solar",
            ],
            "latitude": [
                14.0,
                15.0,
                40.0,
                1.0,
            ],
            "longitude": [
                121.0,
                120.0,
                -100.0,
                1.0,
            ],
        }
    )


def build_owid() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "iso_code": [
                "PHL",
                "USA",
            ],
            "owid_country": [
                "Philippines",
                "United States",
            ],
            "year": [
                2019,
                2019,
            ],
            "co2": [
                142.601,
                5250.0,
            ],
            "co2_per_capita": [
                1.287,
                15.5,
            ],
        }
    )


def build_world_bank() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "iso_code": [
                "PHL",
                "USA",
            ],
            "wb_country": [
                "Philippines",
                "United States",
            ],
            "wb_year": [
                2019,
                2019,
            ],
            "wb_gdp_current_usd": [
                376_823_402_239.136,
                21_380_976_119_000.0,
            ],
            "wb_population": [
                110_804_683.0,
                328_329_953.0,
            ],
            "wb_gdp_per_capita_current_usd": [
                3400.78949767074,
                65120.394663,
            ],
        }
    )


def test_integrate_sources_preserves_plant_rows():
    plants = build_plants()

    result = integrate_sources(
        plants,
        build_owid(),
        build_world_bank(),
    )

    assert len(result) == len(plants)

    assert result["gppd_idnr"].nunique() == (
        plants["gppd_idnr"].nunique()
    )

    assert set(result["gppd_idnr"]) == set(
        plants["gppd_idnr"]
    )


def test_integrate_sources_adds_capacity_features():
    result = integrate_sources(
        build_plants(),
        build_owid(),
        build_world_bank(),
    )

    expected = {
        "total_installed_capacity_mw",
        "country_primary_fuel_capacity_mw",
        "country_primary_fuel_capacity_share_pct",
        "fossil_share_pct",
        "renewable_share_pct",
    }

    assert expected <= set(result.columns)


def test_integrate_sources_merges_owid():
    result = integrate_sources(
        build_plants(),
        build_owid(),
        build_world_bank(),
    )

    phl = result[
        result["country"] == "PHL"
    ]

    assert phl["owid_2019_matched"].all()

    assert (
        phl["owid_country"]
        == "Philippines"
    ).all()

    assert (
        phl["co2"]
        .sub(142.601)
        .abs()
        .lt(1e-9)
        .all()
    )


def test_integrate_sources_merges_world_bank():
    result = integrate_sources(
        build_plants(),
        build_owid(),
        build_world_bank(),
    )

    phl = result[
        result["country"] == "PHL"
    ]

    assert phl["wb_2019_matched"].all()

    assert (
        phl["wb_country"]
        == "Philippines"
    ).all()

    assert phl[
        "wb_population"
    ].notna().all()


def test_unmatched_country_is_preserved():
    result = integrate_sources(
        build_plants(),
        build_owid(),
        build_world_bank(),
    )

    unmatched = result[
        result["country"] == "ZZZ"
    ].iloc[0]

    assert unmatched["gppd_idnr"] == "ZZZ001"

    assert not unmatched[
        "owid_2019_matched"
    ]

    assert not unmatched[
        "wb_2019_matched"
    ]

    assert pd.isna(
        unmatched["co2"]
    )

    assert pd.isna(
        unmatched["wb_population"]
    )


def test_merge_indicators_are_not_exported():
    result = integrate_sources(
        build_plants(),
        build_owid(),
        build_world_bank(),
    )

    assert "_owid_merge" not in result.columns
    assert "_wb_merge" not in result.columns


def test_duplicate_owid_key_is_rejected():
    owid = build_owid()

    owid = pd.concat(
        [
            owid,
            owid.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="duplicate iso_code values",
    ):
        integrate_sources(
            build_plants(),
            owid,
            build_world_bank(),
        )


def test_duplicate_world_bank_key_is_rejected():
    world_bank = build_world_bank()

    world_bank = pd.concat(
        [
            world_bank,
            world_bank.iloc[[0]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="duplicate iso_code values",
    ):
        integrate_sources(
            build_plants(),
            build_owid(),
            world_bank,
        )


def test_missing_required_source_column_is_rejected():
    owid = build_owid().drop(
        columns=["co2"]
    )

    with pytest.raises(
        ValueError,
        match="OWID staging data is missing required columns",
    ):
        integrate_sources(
            build_plants(),
            owid,
            build_world_bank(),
        )


def test_integrate_sources_does_not_mutate_inputs():
    plants = build_plants()
    owid = build_owid()
    world_bank = build_world_bank()

    plants_original = plants.copy(
        deep=True
    )

    owid_original = owid.copy(
        deep=True
    )

    world_bank_original = (
        world_bank.copy(
            deep=True
        )
    )

    integrate_sources(
        plants,
        owid,
        world_bank,
    )

    pd.testing.assert_frame_equal(
        plants,
        plants_original,
    )

    pd.testing.assert_frame_equal(
        owid,
        owid_original,
    )

    pd.testing.assert_frame_equal(
        world_bank,
        world_bank_original,
    )


def test_build_curated_dataset_writes_parquet(
    tmp_path,
):
    plants_path = (
        tmp_path
        / "stg_plants.parquet"
    )

    owid_path = (
        tmp_path
        / "stg_owid_2019.parquet"
    )

    world_bank_path = (
        tmp_path
        / "stg_world_bank_2019.parquet"
    )

    output_path = (
        tmp_path
        / "eta_curated_2019.parquet"
    )

    build_plants().to_parquet(
        plants_path,
        index=False,
    )

    build_owid().to_parquet(
        owid_path,
        index=False,
    )

    build_world_bank().to_parquet(
        world_bank_path,
        index=False,
    )

    result = build_curated_dataset(
        plants_path=plants_path,
        owid_path=owid_path,
        world_bank_path=world_bank_path,
        output_path=output_path,
    )

    assert output_path.exists()
    assert len(result) == 4

    saved = pd.read_parquet(
        output_path
    )

    assert len(saved) == len(result)

    assert set(
        saved["gppd_idnr"]
    ) == set(
        result["gppd_idnr"]
    )


def test_build_curated_dataset_missing_file_raises(
    tmp_path,
):
    with pytest.raises(
        FileNotFoundError,
        match="Missing staging file",
    ):
        build_curated_dataset(
            plants_path=(
                tmp_path
                / "missing_plants.parquet"
            ),
            owid_path=(
                tmp_path
                / "missing_owid.parquet"
            ),
            world_bank_path=(
                tmp_path
                / "missing_wb.parquet"
            ),
            output_path=(
                tmp_path
                / "output.parquet"
            ),
        )