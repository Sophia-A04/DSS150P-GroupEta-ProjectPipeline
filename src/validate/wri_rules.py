from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from . import checks as c
from .reporting import find_raw_files

SOURCE_NAME = "wri_raw"

PRIMARY_FUELS = [
    "Hydro", "Solar", "Gas", "Other", "Oil", "Wind", "Nuclear", "Coal", "Waste",
    "Biomass", "Wave and Tidal", "Petcoke", "Geothermal", "Storage", "Cogeneration",
]
REQUIRED_COLUMNS = [
    "country", "country_long", "name", "gppd_idnr", "capacity_mw", "latitude",
    "longitude", "primary_fuel", "commissioning_year", "owner", "source",
    "generation_gwh_2019",
]
NOT_NULL = ["country", "country_long", "name", "gppd_idnr", "capacity_mw",
            "latitude", "longitude", "primary_fuel"]


def locate() -> List[Path]:
    return find_raw_files(".csv", ("global_power", "gppd", "power_plant", "wri"))


def load(paths: List[Path]) -> pd.DataFrame:
    return pd.read_csv(paths[0], low_memory=False)


def validate(df: pd.DataFrame) -> list:
    s = SOURCE_NAME
    return [
        c.check_schema(df, s, REQUIRED_COLUMNS),
        c.check_dtypes(df, s, {"capacity_mw": "numeric", "latitude": "numeric",
                               "longitude": "numeric", "commissioning_year": "numeric",
                               "country": "string", "gppd_idnr": "string",
                               "primary_fuel": "string"}),
        c.check_not_null(df, s, NOT_NULL),
        c.check_null_rate(df, s, "commissioning_year", 0.60),
        c.check_null_rate(df, s, "owner", 0.50),
        c.check_unique(df, s, "gppd_idnr"),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "country"),
        c.check_accepted_values(df, s, "primary_fuel", PRIMARY_FUELS),
        c.check_range(df, s, "capacity_mw", min_value=0, max_value=25000, inclusive_min=False),
        c.check_range(df, s, "latitude", -90, 90),
        c.check_range(df, s, "longitude", -180, 180),
        c.check_range(df, s, "commissioning_year", 1800, 2026),
        c.check_range(df, s, "generation_gwh_2019", min_value=0, severity="warning"),
        c.check_row_count(df, s, min_rows=10_000, max_rows=100_000),
        c.check_contains_values(df, s, "country", ["PHL"]),
    ]