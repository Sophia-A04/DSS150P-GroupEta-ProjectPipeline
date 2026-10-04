from __future__ import annotations

import pandas as pd

from . import checks as c
from .wri_rules import PRIMARY_FUELS

PLANTS = "stg_plants"
OWID = "stg_owid_2019"
WB = "stg_world_bank_2019"
CROSS = "stg_cross_table"

PLANTS_REQUIRED = ["country", "country_long", "name", "gppd_idnr", "capacity_mw",
                   "primary_fuel", "latitude", "longitude"]
OWID_REQUIRED = ["owid_country", "iso_code", "year", "co2", "co2_per_capita"]
OWID_FORBIDDEN = ["population", "gdp"]
WB_VALUE_COLS = ["wb_gdp_current_usd", "wb_population", "wb_gdp_per_capita_current_usd"]
WB_REQUIRED = ["iso_code", "wb_country", "wb_year"] + WB_VALUE_COLS
SNAPSHOT_YEAR = 2019


def validate_plants(df: pd.DataFrame, raw_row_count: int | None = None) -> list:
    s = PLANTS
    results = [
        c.check_schema(df, s, PLANTS_REQUIRED),
        c.check_dtypes(df, s, {"capacity_mw": "numeric", "latitude": "numeric",
                               "longitude": "numeric", "country": "string",
                               "gppd_idnr": "string", "primary_fuel": "string"}),
        c.check_not_null(df, s, ["country", "gppd_idnr", "primary_fuel", "capacity_mw"]),
        c.check_unique(df, s, "gppd_idnr"),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "country"),
        c.check_accepted_values(df, s, "primary_fuel", PRIMARY_FUELS),
        c.check_range(df, s, "capacity_mw", min_value=0, max_value=25000, inclusive_min=False),
        c.check_row_count(df, s, min_rows=10_000, max_rows=100_000),
        c.check_contains_values(df, s, "country", ["PHL"]),
    ]
    if raw_row_count is not None:
        results.append(c.check_row_count_preserved(df, s, raw_row_count, tolerance=0.05))
    return results


def validate_owid(df: pd.DataFrame) -> list:
    s = OWID
    return [
        c.check_schema(df, s, OWID_REQUIRED),
        c.check_columns_absent(df, s, OWID_FORBIDDEN),
        c.check_dtypes(df, s, {"year": "numeric", "co2": "numeric",
                               "co2_per_capita": "numeric", "iso_code": "string"}),
        c.check_not_null(df, s, ["iso_code", "owid_country", "year"]),
        c.check_unique(df, s, "iso_code"),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "iso_code"),
        c.check_accepted_values(df, s, "year", [SNAPSHOT_YEAR]),
        c.check_range(df, s, "co2", 0),
        c.check_range(df, s, "co2_per_capita", 0),
        c.check_row_count(df, s, min_rows=100, max_rows=400),
        c.check_contains_values(df, s, "iso_code", ["PHL"]),
    ]


def validate_world_bank(df: pd.DataFrame) -> list:
    s = WB
    phl_missing = 0
    if {"iso_code", *WB_VALUE_COLS} <= set(df.columns):
        phl = df[df["iso_code"] == "PHL"]
        phl_missing = int(phl[WB_VALUE_COLS].isna().any(axis=1).sum())
    return [
        c.check_schema(df, s, WB_REQUIRED),
        c.check_dtypes(df, s, {"iso_code": "string", "wb_gdp_current_usd": "numeric",
                               "wb_population": "numeric",
                               "wb_gdp_per_capita_current_usd": "numeric"}),
        c.check_not_null(df, s, ["iso_code", "wb_country", "wb_year"]),
        c.check_unique(df, s, "iso_code"),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "iso_code"),
        c.check_accepted_values(df, s, "wb_year", [SNAPSHOT_YEAR, str(SNAPSHOT_YEAR)]),
        c.check_range(df, s, "wb_gdp_current_usd", 0),
        c.check_range(df, s, "wb_population", 0),
        c.check_range(df, s, "wb_gdp_per_capita_current_usd", 0),
        c.check_row_count(df, s, min_rows=100, max_rows=400),
        c.check_contains_values(df, s, "iso_code", ["PHL"]),
        c.check_rule(s, "phl_indicator_values_populated", phl_missing,
                     "Philippines is missing one or more World Bank indicator values"),
    ]


def validate_cross_table(plants: pd.DataFrame, owid: pd.DataFrame, wb: pd.DataFrame) -> list:
    s = CROSS
    return [
        c.check_referential_integrity(plants, owid, s, "country", "iso_code", severity="warning"),
        c.check_referential_integrity(plants, wb, s, "country", "iso_code", severity="warning"),
    ]