from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from . import checks as c
from .reporting import find_raw_files

SOURCE_NAME = "owid_raw"

REQUIRED_COLUMNS = ["country", "year", "iso_code", "population", "gdp", "co2",
                    "co2_per_capita", "coal_co2", "methane", "share_global_co2"]
NOT_NULL = ["country", "year"]


def locate() -> List[Path]:
    return find_raw_files(".csv", ("owid", "co2"))


def load(paths: List[Path]) -> pd.DataFrame:
    return pd.read_csv(paths[0], low_memory=False)


def validate(df: pd.DataFrame) -> list:
    s = SOURCE_NAME
    return [
        c.check_schema(df, s, REQUIRED_COLUMNS),
        c.check_dtypes(df, s, {"year": "numeric", "population": "numeric", "gdp": "numeric",
                               "co2": "numeric", "country": "string", "iso_code": "string"}),
        c.check_not_null(df, s, NOT_NULL),
        c.check_null_rate(df, s, "iso_code", 0.25),
        c.check_unique(df, s, ["country", "year"]),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "iso_code", allow_null=True),
        c.check_range(df, s, "year", 1750, 2026),
        c.check_range(df, s, "population", 0),
        c.check_range(df, s, "gdp", 0),
        c.check_range(df, s, "co2", 0),
        c.check_range(df, s, "co2_per_capita", 0),
        c.check_range(df, s, "share_global_co2", 0, 100),
        c.check_row_count(df, s, min_rows=10_000, max_rows=500_000),
        c.check_contains_values(df, s, "iso_code", ["PHL"]),
        c.check_contains_values(df, s, "year", [2019]),
    ]