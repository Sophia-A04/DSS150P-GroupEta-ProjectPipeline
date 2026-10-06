from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from src.load.postgres_loader import (
    apply_schema,
    get_connection,
)
from src.transform.capacity_features import (
    FOSSIL_FUELS,
    RENEWABLE_FUELS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CURATED_PATH = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "eta_curated_2019.parquet"
)

SNAPSHOT_YEAR = 2019

GENERATION_YEARS = range(
    2013,
    2020,
)


def _db_value(value):
    """Convert pandas/numpy values into psycopg2-friendly Python values."""
    if pd.isna(value):
        return None

    if isinstance(
        value,
        np.generic,
    ):
        return value.item()

    return value


def _records(
    df: pd.DataFrame,
    columns: list[str],
) -> list[tuple]:
    """Convert selected DataFrame columns into database-safe tuples."""
    return [
        tuple(
            _db_value(value)
            for value in row
        )
        for row in df[
            columns
        ].itertuples(
            index=False,
            name=None,
        )
    ]


def classify_fuel(
    fuel_name: str,
) -> str:
    """Map a primary fuel to the project fuel grouping."""
    if fuel_name in FOSSIL_FUELS:
        return "fossil"

    if fuel_name in RENEWABLE_FUELS:
        return "renewable"

    return "other_or_unclassified"


def build_countries(
    curated: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per WRI country."""
    countries = (
        curated[
            [
                "country",
                "country_long",
                "owid_country",
                "wb_country",
            ]
        ]
        .groupby(
            "country",
            as_index=False,
        )
        .agg(
            {
                "country_long": "first",
                "owid_country": "first",
                "wb_country": "first",
            }
        )
        .rename(
            columns={
                "country":
                    "country_code",
                "country_long":
                    "country_name",
                "owid_country":
                    "owid_country_name",
                "wb_country":
                    "wb_country_name",
            }
        )
    )

    return countries


def build_fuel_types(
    curated: pd.DataFrame,
) -> pd.DataFrame:
    """Build the standardized fuel lookup."""
    fuels = (
        curated[
            ["primary_fuel"]
        ]
        .drop_duplicates()
        .dropna()
        .rename(
            columns={
                "primary_fuel":
                    "fuel_name"
            }
        )
        .sort_values(
            "fuel_name"
        )
        .reset_index(
            drop=True
        )
    )

    fuels[
        "fuel_group"
    ] = fuels[
        "fuel_name"
    ].map(
        classify_fuel
    )

    return fuels


def build_power_plants(
    curated: pd.DataFrame,
    fuel_ids: dict[str, int],
) -> pd.DataFrame:
    """Build one normalized row per real power plant."""
    plants = (
        curated[
            [
                "gppd_idnr",
                "country",
                "name",
                "capacity_mw",
                "latitude",
                "longitude",
                "primary_fuel",
                "other_fuel1",
                "other_fuel2",
                "other_fuel3",
                "commissioning_year",
                "owner",
                "source",
                "url",
                "geolocation_source",
                "wepp_id",
                "year_of_capacity_data",
            ]
        ]
        .copy()
    )

    plants[
        "primary_fuel_id"
    ] = plants[
        "primary_fuel"
    ].map(
        fuel_ids
    )

    if plants[
        "primary_fuel_id"
    ].isna().any():
        raise ValueError(
            "Some power plants could not be mapped "
            "to a PostgreSQL fuel_id."
        )

    plants = plants.rename(
        columns={
            "country":
                "country_code",
            "name":
                "plant_name",
            "url":
                "source_url",
        }
    )

    plants[
        "commissioning_year"
    ] = pd.to_numeric(
        plants[
            "commissioning_year"
        ],
        errors="coerce",
    )

    plants[
        "year_of_capacity_data"
    ] = pd.to_numeric(
        plants[
            "year_of_capacity_data"
        ],
        errors="coerce",
    ).astype(
        "Int64"
    )

    plants[
        "primary_fuel_id"
    ] = plants[
        "primary_fuel_id"
    ].astype(
        "Int64"
    )

    return plants.drop(
        columns=[
            "primary_fuel"
        ]
    )


def build_plant_generation(
    curated: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert wide yearly generation columns into
    one row per plant per year.
    """
    frames = []

    for year in GENERATION_YEARS:
        actual_column = (
            f"generation_gwh_{year}"
        )

        estimated_column = (
            f"estimated_generation_gwh_{year}"
        )

        note_column = (
            f"estimated_generation_note_{year}"
        )

        frame = pd.DataFrame(
            {
                "gppd_idnr":
                    curated[
                        "gppd_idnr"
                    ],
                "generation_year":
                    year,
                "generation_gwh":
                    (
                        curated[
                            actual_column
                        ]
                        if actual_column
                        in curated.columns
                        else np.nan
                    ),
                "estimated_generation_gwh":
                    (
                        curated[
                            estimated_column
                        ]
                        if estimated_column
                        in curated.columns
                        else np.nan
                    ),
                "generation_data_source":
                    curated[
                        "generation_data_source"
                    ],
                "estimation_note":
                    (
                        curated[
                            note_column
                        ]
                        if note_column
                        in curated.columns
                        else None
                    ),
            }
        )

        useful = (
            frame[
                "generation_gwh"
            ].notna()
            | frame[
                "estimated_generation_gwh"
            ].notna()
            | frame[
                "estimation_note"
            ].notna()
        )

        frames.append(
            frame.loc[
                useful
            ]
        )

    if not frames:
        return pd.DataFrame(
            columns=[
                "gppd_idnr",
                "generation_year",
                "generation_gwh",
                "estimated_generation_gwh",
                "generation_data_source",
                "estimation_note",
            ]
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


def build_country_emissions(
    curated: pd.DataFrame,
) -> pd.DataFrame:
    """Build one OWID emissions record per matched country-year."""
    columns = [
        "country",
        "year",
        "co2",
        "co2_per_capita",
        "coal_co2",
        "gas_co2",
        "oil_co2",
        "methane",
        "nitrous_oxide",
        "total_ghg",
        "primary_energy_consumption",
        "share_global_co2",
    ]

    matched = curated[
        curated[
            "owid_2019_matched"
        ].fillna(False)
    ]

    emissions = (
        matched[
            columns
        ]
        .drop_duplicates(
            subset=[
                "country",
                "year",
            ]
        )
        .rename(
            columns={
                "country":
                    "country_code"
            }
        )
        .reset_index(
            drop=True
        )
    )

    emissions[
        "year"
    ] = pd.to_numeric(
        emissions["year"],
        errors="coerce",
    ).astype(
        "Int64"
    )

    return emissions


def build_country_economic_indicators(
    curated: pd.DataFrame,
) -> pd.DataFrame:
    """Build one World Bank indicator record per matched country-year."""
    matched = curated[
        curated[
            "wb_2019_matched"
        ].fillna(False)
    ]

    economic = (
        matched[
            [
                "country",
                "wb_year",
                "wb_gdp_current_usd",
                "wb_population",
                "wb_gdp_per_capita_current_usd",
            ]
        ]
        .drop_duplicates(
            subset=[
                "country",
                "wb_year",
            ]
        )
        .rename(
            columns={
                "country":
                    "country_code",
                "wb_year":
                    "year",
                "wb_gdp_current_usd":
                    "gdp_current_usd",
                "wb_population":
                    "population",
                "wb_gdp_per_capita_current_usd":
                    "gdp_per_capita_current_usd",
            }
        )
        .reset_index(
            drop=True
        )
    )

    economic[
        "year"
    ] = pd.to_numeric(
        economic["year"],
        errors="coerce",
    ).astype(
        "Int64"
    )

    economic[
        "population"
    ] = pd.to_numeric(
        economic[
            "population"
        ],
        errors="coerce",
    ).astype(
        "Int64"
    )

    return economic


def build_country_fuel_capacity(
    curated: pd.DataFrame,
    fuel_ids: dict[str, int],
) -> pd.DataFrame:
    """Build one derived capacity record per country and primary fuel."""
    capacity = (
        curated[
            [
                "country",
                "primary_fuel",
                "country_primary_fuel_plant_count",
                "country_primary_fuel_capacity_mw",
                "country_primary_fuel_capacity_share_pct",
            ]
        ]
        .drop_duplicates(
            subset=[
                "country",
                "primary_fuel",
            ]
        )
        .copy()
    )

    capacity[
        "fuel_id"
    ] = capacity[
        "primary_fuel"
    ].map(
        fuel_ids
    )

    if capacity[
        "fuel_id"
    ].isna().any():
        raise ValueError(
            "Some country-fuel capacity rows "
            "could not be mapped to fuel_id."
        )

    capacity[
        "snapshot_year"
    ] = SNAPSHOT_YEAR

    capacity = capacity.rename(
        columns={
            "country":
                "country_code",
            "country_primary_fuel_plant_count":
                "plant_count",
            "country_primary_fuel_capacity_mw":
                "installed_capacity_mw",
            "country_primary_fuel_capacity_share_pct":
                "capacity_share_pct",
        }
    )

    capacity[
        "fuel_id"
    ] = capacity[
        "fuel_id"
    ].astype(
        "Int64"
    )

    capacity[
        "plant_count"
    ] = pd.to_numeric(
        capacity[
            "plant_count"
        ],
        errors="raise",
    ).astype(
        "Int64"
    )

    return capacity[
        [
            "country_code",
            "fuel_id",
            "snapshot_year",
            "plant_count",
            "installed_capacity_mw",
            "capacity_share_pct",
        ]
    ]


def _execute_values(
    cursor,
    sql: str,
    frame: pd.DataFrame,
    columns: list[str],
) -> None:
    """Bulk-execute an INSERT/UPSERT statement."""
    rows = _records(
        frame,
        columns,
    )

    if rows:
        execute_values(
            cursor,
            sql,
            rows,
            page_size=1000,
        )


def _load_countries(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "country_code",
        "country_name",
        "owid_country_name",
        "wb_country_name",
    ]

    sql = """
        INSERT INTO countries (
            country_code,
            country_name,
            owid_country_name,
            wb_country_name
        )
        VALUES %s
        ON CONFLICT (country_code)
        DO UPDATE SET
            country_name = EXCLUDED.country_name,
            owid_country_name = EXCLUDED.owid_country_name,
            wb_country_name = EXCLUDED.wb_country_name;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def _load_fuels(
    cursor,
    frame: pd.DataFrame,
) -> dict[str, int]:
    sql = """
        INSERT INTO fuel_types (
            fuel_name,
            fuel_group
        )
        VALUES %s
        ON CONFLICT (fuel_name)
        DO UPDATE SET
            fuel_group = EXCLUDED.fuel_group;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        [
            "fuel_name",
            "fuel_group",
        ],
    )

    cursor.execute(
        """
        SELECT fuel_id, fuel_name
        FROM fuel_types;
        """
    )

    return {
        fuel_name: fuel_id
        for fuel_id, fuel_name
        in cursor.fetchall()
    }


def _load_power_plants(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "gppd_idnr",
        "country_code",
        "plant_name",
        "capacity_mw",
        "latitude",
        "longitude",
        "primary_fuel_id",
        "other_fuel1",
        "other_fuel2",
        "other_fuel3",
        "commissioning_year",
        "owner",
        "source",
        "source_url",
        "geolocation_source",
        "wepp_id",
        "year_of_capacity_data",
    ]

    sql = """
        INSERT INTO power_plants (
            gppd_idnr,
            country_code,
            plant_name,
            capacity_mw,
            latitude,
            longitude,
            primary_fuel_id,
            other_fuel1,
            other_fuel2,
            other_fuel3,
            commissioning_year,
            owner,
            source,
            source_url,
            geolocation_source,
            wepp_id,
            year_of_capacity_data
        )
        VALUES %s
        ON CONFLICT (gppd_idnr)
        DO UPDATE SET
            country_code = EXCLUDED.country_code,
            plant_name = EXCLUDED.plant_name,
            capacity_mw = EXCLUDED.capacity_mw,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            primary_fuel_id = EXCLUDED.primary_fuel_id,
            other_fuel1 = EXCLUDED.other_fuel1,
            other_fuel2 = EXCLUDED.other_fuel2,
            other_fuel3 = EXCLUDED.other_fuel3,
            commissioning_year = EXCLUDED.commissioning_year,
            owner = EXCLUDED.owner,
            source = EXCLUDED.source,
            source_url = EXCLUDED.source_url,
            geolocation_source = EXCLUDED.geolocation_source,
            wepp_id = EXCLUDED.wepp_id,
            year_of_capacity_data = EXCLUDED.year_of_capacity_data;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def _load_generation(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "gppd_idnr",
        "generation_year",
        "generation_gwh",
        "estimated_generation_gwh",
        "generation_data_source",
        "estimation_note",
    ]

    sql = """
        INSERT INTO plant_generation (
            gppd_idnr,
            generation_year,
            generation_gwh,
            estimated_generation_gwh,
            generation_data_source,
            estimation_note
        )
        VALUES %s
        ON CONFLICT (
            gppd_idnr,
            generation_year
        )
        DO UPDATE SET
            generation_gwh = EXCLUDED.generation_gwh,
            estimated_generation_gwh =
                EXCLUDED.estimated_generation_gwh,
            generation_data_source =
                EXCLUDED.generation_data_source,
            estimation_note =
                EXCLUDED.estimation_note;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def _load_emissions(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "country_code",
        "year",
        "co2",
        "co2_per_capita",
        "coal_co2",
        "gas_co2",
        "oil_co2",
        "methane",
        "nitrous_oxide",
        "total_ghg",
        "primary_energy_consumption",
        "share_global_co2",
    ]

    sql = """
        INSERT INTO country_emissions (
            country_code,
            year,
            co2,
            co2_per_capita,
            coal_co2,
            gas_co2,
            oil_co2,
            methane,
            nitrous_oxide,
            total_ghg,
            primary_energy_consumption,
            share_global_co2
        )
        VALUES %s
        ON CONFLICT (
            country_code,
            year
        )
        DO UPDATE SET
            co2 = EXCLUDED.co2,
            co2_per_capita = EXCLUDED.co2_per_capita,
            coal_co2 = EXCLUDED.coal_co2,
            gas_co2 = EXCLUDED.gas_co2,
            oil_co2 = EXCLUDED.oil_co2,
            methane = EXCLUDED.methane,
            nitrous_oxide = EXCLUDED.nitrous_oxide,
            total_ghg = EXCLUDED.total_ghg,
            primary_energy_consumption =
                EXCLUDED.primary_energy_consumption,
            share_global_co2 =
                EXCLUDED.share_global_co2;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def _load_economic(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "country_code",
        "year",
        "gdp_current_usd",
        "population",
        "gdp_per_capita_current_usd",
    ]

    sql = """
        INSERT INTO country_economic_indicators (
            country_code,
            year,
            gdp_current_usd,
            population,
            gdp_per_capita_current_usd
        )
        VALUES %s
        ON CONFLICT (
            country_code,
            year
        )
        DO UPDATE SET
            gdp_current_usd =
                EXCLUDED.gdp_current_usd,
            population =
                EXCLUDED.population,
            gdp_per_capita_current_usd =
                EXCLUDED.gdp_per_capita_current_usd;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def _load_capacity(
    cursor,
    frame: pd.DataFrame,
) -> None:
    columns = [
        "country_code",
        "fuel_id",
        "snapshot_year",
        "plant_count",
        "installed_capacity_mw",
        "capacity_share_pct",
    ]

    sql = """
        INSERT INTO country_fuel_capacity (
            country_code,
            fuel_id,
            snapshot_year,
            plant_count,
            installed_capacity_mw,
            capacity_share_pct
        )
        VALUES %s
        ON CONFLICT (
            country_code,
            fuel_id,
            snapshot_year
        )
        DO UPDATE SET
            plant_count =
                EXCLUDED.plant_count,
            installed_capacity_mw =
                EXCLUDED.installed_capacity_mw,
            capacity_share_pct =
                EXCLUDED.capacity_share_pct;
    """

    _execute_values(
        cursor,
        sql,
        frame,
        columns,
    )


def table_counts(
    connection,
) -> dict[str, int]:
    """Return row counts for all seven project tables."""
    tables = [
        "countries",
        "fuel_types",
        "power_plants",
        "plant_generation",
        "country_emissions",
        "country_economic_indicators",
        "country_fuel_capacity",
    ]

    counts = {}

    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table};"
            )

            counts[
                table
            ] = cursor.fetchone()[0]

    return counts


def load_curated_to_postgres(
    connection,
    curated_path: str | Path = DEFAULT_CURATED_PATH,
) -> dict[str, int]:
    """
    Normalize the curated Parquet dataset and load it
    into the seven PostgreSQL project tables.

    UPSERT behavior makes repeated executions idempotent.
    """
    curated_path = Path(
        curated_path
    )

    if not curated_path.exists():
        raise FileNotFoundError(
            f"Curated dataset not found: {curated_path}"
        )

    curated = pd.read_parquet(
        curated_path
    )

    countries = build_countries(
        curated
    )

    fuel_types = build_fuel_types(
        curated
    )

    try:
        with connection.cursor() as cursor:
            _load_countries(
                cursor,
                countries,
            )

            fuel_ids = _load_fuels(
                cursor,
                fuel_types,
            )

            power_plants = build_power_plants(
                curated,
                fuel_ids,
            )

            generation = build_plant_generation(
                curated
            )

            emissions = build_country_emissions(
                curated
            )

            economic = (
                build_country_economic_indicators(
                    curated
                )
            )

            capacity = (
                build_country_fuel_capacity(
                    curated,
                    fuel_ids,
                )
            )

            _load_power_plants(
                cursor,
                power_plants,
            )

            _load_generation(
                cursor,
                generation,
            )

            _load_emissions(
                cursor,
                emissions,
            )

            _load_economic(
                cursor,
                economic,
            )

            _load_capacity(
                cursor,
                capacity,
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    return table_counts(
        connection
    )


def run_postgres_load(
    curated_path: str | Path = DEFAULT_CURATED_PATH,
) -> dict[str, int]:
    """
    Create/verify the schema and load the curated dataset
    into PostgreSQL.
    """
    connection = get_connection()

    try:
        apply_schema(
            connection
        )

        return load_curated_to_postgres(
            connection,
            curated_path,
        )

    finally:
        connection.close()


def main() -> int:
    try:
        counts = run_postgres_load()

    except Exception as error:
        print(
            "PostgreSQL data load FAILED:"
        )
        print(error)
        return 1

    print(
        "\n=== POSTGRESQL DATA LOAD ==="
    )

    for table, count in counts.items():
        print(
            f"{table}: {count}"
        )

    print(
        "\nPostgreSQL data load PASSED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )