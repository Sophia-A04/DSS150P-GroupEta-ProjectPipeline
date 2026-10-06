import pandas as pd

from src.load.postgres_data_loader import (
    build_countries,
    build_country_economic_indicators,
    build_country_emissions,
    build_country_fuel_capacity,
    build_fuel_types,
    build_plant_generation,
    build_power_plants,
    classify_fuel,
)


def build_curated():
    return pd.DataFrame(
        {
            "country": [
                "PHL",
                "PHL",
                "USA",
            ],
            "country_long": [
                "Philippines",
                "Philippines",
                "United States",
            ],
            "owid_country": [
                "Philippines",
                "Philippines",
                "United States",
            ],
            "wb_country": [
                "Philippines",
                "Philippines",
                "United States",
            ],
            "gppd_idnr": [
                "PHL001",
                "PHL002",
                "USA001",
            ],
            "name": [
                "Plant A",
                "Plant B",
                "Plant C",
            ],
            "capacity_mw": [
                100.0,
                300.0,
                500.0,
            ],
            "latitude": [
                14.0,
                15.0,
                40.0,
            ],
            "longitude": [
                121.0,
                120.0,
                -100.0,
            ],
            "primary_fuel": [
                "Coal",
                "Hydro",
                "Gas",
            ],
            "other_fuel1": [
                None,
                None,
                None,
            ],
            "other_fuel2": [
                None,
                None,
                None,
            ],
            "other_fuel3": [
                None,
                None,
                None,
            ],
            "commissioning_year": [
                1990,
                2000,
                2010,
            ],
            "owner": [
                "A",
                "B",
                "C",
            ],
            "source": [
                "WRI",
                "WRI",
                "WRI",
            ],
            "url": [
                "a",
                "b",
                "c",
            ],
            "geolocation_source": [
                "x",
                "x",
                "x",
            ],
            "wepp_id": [
                None,
                None,
                None,
            ],
            "year_of_capacity_data": [
                2019,
                2019,
                2019,
            ],
            "generation_gwh_2013": [
                1000.0,
                None,
                2000.0,
            ],
            "generation_data_source": [
                "source",
                "source",
                "source",
            ],
            "estimated_generation_gwh_2013": [
                None,
                500.0,
                None,
            ],
            "estimated_generation_note_2013": [
                None,
                "estimated",
                None,
            ],
            "year": [
                2019,
                2019,
                2019,
            ],
            "co2": [
                142.6,
                142.6,
                5250.0,
            ],
            "co2_per_capita": [
                1.2,
                1.2,
                15.0,
            ],
            "coal_co2": [
                80.0,
                80.0,
                1000.0,
            ],
            "gas_co2": [
                20.0,
                20.0,
                1500.0,
            ],
            "oil_co2": [
                30.0,
                30.0,
                2000.0,
            ],
            "methane": [
                10.0,
                10.0,
                20.0,
            ],
            "nitrous_oxide": [
                5.0,
                5.0,
                10.0,
            ],
            "total_ghg": [
                200.0,
                200.0,
                6000.0,
            ],
            "primary_energy_consumption": [
                100.0,
                100.0,
                1000.0,
            ],
            "share_global_co2": [
                0.4,
                0.4,
                14.0,
            ],
            "owid_2019_matched": [
                True,
                True,
                True,
            ],
            "wb_year": [
                2019,
                2019,
                2019,
            ],
            "wb_gdp_current_usd": [
                376e9,
                376e9,
                21e12,
            ],
            "wb_population": [
                110_000_000,
                110_000_000,
                328_000_000,
            ],
            "wb_gdp_per_capita_current_usd": [
                3400.0,
                3400.0,
                65000.0,
            ],
            "wb_2019_matched": [
                True,
                True,
                True,
            ],
            "country_primary_fuel_plant_count": [
                1,
                1,
                1,
            ],
            "country_primary_fuel_capacity_mw": [
                100.0,
                300.0,
                500.0,
            ],
            "country_primary_fuel_capacity_share_pct": [
                25.0,
                75.0,
                100.0,
            ],
        }
    )


def test_classify_fuel():
    assert classify_fuel("Coal") == "fossil"
    assert classify_fuel("Hydro") == "renewable"

    assert (
        classify_fuel("Nuclear")
        == "other_or_unclassified"
    )


def test_build_countries():
    result = build_countries(
        build_curated()
    )

    assert len(result) == 2

    assert set(
        result["country_code"]
    ) == {
        "PHL",
        "USA",
    }


def test_build_fuel_types():
    result = build_fuel_types(
        build_curated()
    )

    assert len(result) == 3

    coal = result[
        result["fuel_name"] == "Coal"
    ].iloc[0]

    assert (
        coal["fuel_group"]
        == "fossil"
    )


def test_build_power_plants():
    result = build_power_plants(
        build_curated(),
        {
            "Coal": 1,
            "Hydro": 2,
            "Gas": 3,
        },
    )

    assert len(result) == 3

    assert (
        result[
            "gppd_idnr"
        ].nunique()
        == 3
    )

    assert (
        "primary_fuel"
        not in result.columns
    )

    assert (
        "primary_fuel_id"
        in result.columns
    )


def test_build_plant_generation():
    result = build_plant_generation(
        build_curated()
    )

    rows_2013 = result[
        result[
            "generation_year"
        ] == 2013
    ]

    assert len(rows_2013) == 3

    assert (
        rows_2013[
            "gppd_idnr"
        ].nunique()
        == 3
    )


def test_build_country_emissions():
    result = build_country_emissions(
        build_curated()
    )

    assert len(result) == 2

    assert (
        result["year"]
        .eq(2019)
        .all()
    )


def test_build_country_economic_indicators():
    result = (
        build_country_economic_indicators(
            build_curated()
        )
    )

    assert len(result) == 2

    assert (
        result["year"]
        .eq(2019)
        .all()
    )


def test_build_country_fuel_capacity():
    result = build_country_fuel_capacity(
        build_curated(),
        {
            "Coal": 1,
            "Hydro": 2,
            "Gas": 3,
        },
    )

    assert len(result) == 3

    assert (
        result[
            "snapshot_year"
        ]
        .eq(2019)
        .all()
    )


def test_build_power_plants_preserves_fractional_commissioning_year():
    curated = build_curated()

    curated[
        "commissioning_year"
    ] = curated[
        "commissioning_year"
    ].astype(float)

    curated.loc[
        curated[
            "gppd_idnr"
        ] == "PHL001",
        "commissioning_year",
    ] = 1997.5

    result = build_power_plants(
        curated,
        {
            "Coal": 1,
            "Hydro": 2,
            "Gas": 3,
        },
    )

    row = result[
        result[
            "gppd_idnr"
        ] == "PHL001"
    ].iloc[0]

    assert (
        row[
            "commissioning_year"
        ]
        == 1997.5
    )