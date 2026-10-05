from __future__ import annotations

import pandas as pd
import pytest

from src.transform.capacity_features import (
    add_capacity_features_to_plants,
    build_country_capacity_features,
    build_country_fuel_capacity,
    build_country_totals,
)


def build_plants() -> pd.DataFrame:
    """Small plant-level fixture with fossil, renewable, and other fuels."""
    return pd.DataFrame(
        {
            "country": [
                "PHL",
                "PHL",
                "PHL",
                "PHL",
                "USA",
                "USA",
            ],
            "gppd_idnr": [
                "PHL001",
                "PHL002",
                "PHL003",
                "PHL004",
                "USA001",
                "USA002",
            ],
            "capacity_mw": [
                100.0,
                300.0,
                200.0,
                400.0,
                600.0,
                400.0,
            ],
            "primary_fuel": [
                "Coal",
                "Gas",
                "Hydro",
                "Nuclear",
                "Wind",
                "Oil",
            ],
            "name": [
                "Plant 1",
                "Plant 2",
                "Plant 3",
                "Plant 4",
                "Plant 5",
                "Plant 6",
            ],
        }
    )


def test_build_country_totals():
    plants = build_plants()

    result = build_country_totals(plants)

    phl = result[
        result["country"] == "PHL"
    ].iloc[0]

    usa = result[
        result["country"] == "USA"
    ].iloc[0]

    assert phl["total_plant_count"] == 4
    assert phl["total_installed_capacity_mw"] == pytest.approx(1000.0)

    assert usa["total_plant_count"] == 2
    assert usa["total_installed_capacity_mw"] == pytest.approx(1000.0)


def test_build_country_fuel_capacity():
    plants = build_plants()

    result = build_country_fuel_capacity(plants)

    phl_coal = result[
        (result["country"] == "PHL")
        & (result["primary_fuel"] == "Coal")
    ].iloc[0]

    assert phl_coal["plant_count"] == 1
    assert phl_coal["capacity_mw"] == pytest.approx(100.0)
    assert phl_coal["total_installed_capacity_mw"] == pytest.approx(1000.0)
    assert phl_coal["capacity_share_pct"] == pytest.approx(10.0)


def test_country_capacity_features_group_fuels_correctly():
    plants = build_plants()

    result = build_country_capacity_features(plants)

    phl = result[
        result["country"] == "PHL"
    ].iloc[0]

    # Fossil = Coal + Gas = 100 + 300
    assert phl["fossil_capacity_mw"] == pytest.approx(400.0)

    # Renewable = Hydro = 200
    assert phl["renewable_capacity_mw"] == pytest.approx(200.0)

    # Other/unclassified = Nuclear = 400
    assert phl["other_or_unclassified_capacity_mw"] == pytest.approx(400.0)

    assert phl["fossil_share_pct"] == pytest.approx(40.0)
    assert phl["renewable_share_pct"] == pytest.approx(20.0)
    assert phl["other_or_unclassified_share_pct"] == pytest.approx(40.0)


def test_country_capacity_features_include_fuel_specific_columns():
    plants = build_plants()

    result = build_country_capacity_features(plants)

    expected_columns = {
        "Coal_capacity_mw",
        "Coal_share_pct",
        "Gas_capacity_mw",
        "Gas_share_pct",
        "Hydro_capacity_mw",
        "Hydro_share_pct",
        "Nuclear_capacity_mw",
        "Nuclear_share_pct",
    }

    assert expected_columns <= set(result.columns)


def test_fuel_shares_sum_to_approximately_100_per_country():
    plants = build_plants()

    result = build_country_fuel_capacity(plants)

    totals = (
        result
        .groupby("country")["capacity_share_pct"]
        .sum()
    )

    for total in totals:
        assert total == pytest.approx(
            100.0,
            abs=1e-9,
        )


def test_group_shares_sum_to_approximately_100_per_country():
    plants = build_plants()

    result = build_country_capacity_features(plants)

    sums = (
        result["fossil_share_pct"]
        + result["renewable_share_pct"]
        + result["other_or_unclassified_share_pct"]
    )

    for total in sums:
        assert total == pytest.approx(
            100.0,
            abs=1e-9,
        )


def test_add_capacity_features_preserves_plant_grain():
    plants = build_plants()

    result = add_capacity_features_to_plants(plants)

    assert len(result) == len(plants)
    assert result["gppd_idnr"].nunique() == plants["gppd_idnr"].nunique()


def test_add_capacity_features_attaches_plant_primary_fuel_features():
    plants = build_plants()

    result = add_capacity_features_to_plants(plants)

    phl_coal = result[
        result["gppd_idnr"] == "PHL001"
    ].iloc[0]

    phl_hydro = result[
        result["gppd_idnr"] == "PHL003"
    ].iloc[0]

    assert phl_coal["country_primary_fuel_capacity_mw"] == pytest.approx(100.0)
    assert phl_coal[
        "country_primary_fuel_capacity_share_pct"
    ] == pytest.approx(10.0)

    assert phl_hydro["country_primary_fuel_capacity_mw"] == pytest.approx(200.0)
    assert phl_hydro[
        "country_primary_fuel_capacity_share_pct"
    ] == pytest.approx(20.0)


def test_add_capacity_features_preserves_original_columns():
    plants = build_plants()

    result = add_capacity_features_to_plants(plants)

    for column in plants.columns:
        assert column in result.columns


def test_capacity_functions_do_not_mutate_input():
    plants = build_plants()
    original = plants.copy(deep=True)

    add_capacity_features_to_plants(plants)

    pd.testing.assert_frame_equal(
        plants,
        original,
    )


def test_capacity_functions_require_expected_columns():
    plants = build_plants().drop(
        columns=["capacity_mw"]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        build_country_totals(plants)