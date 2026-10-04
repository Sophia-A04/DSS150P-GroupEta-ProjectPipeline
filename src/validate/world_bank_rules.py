from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

import pandas as pd

from . import checks as c
from .reporting import find_raw_files

logger = logging.getLogger("validation")

SOURCE_NAME = "world_bank_raw"
WB_YEAR = "2019"
INDICATORS = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "NY.GDP.PCAP.CD"]
REQUIRED_COLUMNS = ["indicator_id", "indicator_value", "country_id", "country_value",
                    "countryiso3code", "date", "value"]


def locate() -> List[Path]:
    files = find_raw_files(".json", ("world", "wb_", "wb-", "worldbank"))
    if not files:
        return []
    newest_dir = max(files, key=lambda p: p.stat().st_mtime).parent
    return [f for f in files if f.parent == newest_dir]


def _is_response(x) -> bool:
    return (isinstance(x, list) and len(x) == 2 and isinstance(x[0], dict)
            and (x[1] is None or isinstance(x[1], list)))


def load(paths: List[Path]) -> pd.DataFrame:
    frames = []
    for p in paths:
        payload = json.loads(p.read_text(encoding="utf-8"))
        if _is_response(payload):
            responses = [payload]
        elif isinstance(payload, list):
            responses = [r for r in payload if _is_response(r)]
        else:
            responses = []
        if not responses:
            logger.warning("Skipping %s: not a World Bank API response", p.name)
            continue
        for _, records in responses:
            if records:
                df = pd.json_normalize(records, sep="_")
                df["source_file"] = p.name
                frames.append(df)
    if not frames:
        raise ValueError("No World Bank records found in the raw JSON files.")
    return pd.concat(frames, ignore_index=True)


def validate(df: pd.DataFrame) -> list:
    s = SOURCE_NAME
    df = df.copy()
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return [
        c.check_schema(df, s, REQUIRED_COLUMNS),
        c.check_dtypes(df, s, {"value": "numeric", "indicator_id": "string",
                               "countryiso3code": "string", "date": "string"}),
        c.check_not_null(df, s, ["indicator_id", "country_id", "date"]),
        c.check_null_rate(df, s, "value", 0.50),
        c.check_unique(df, s, ["indicator_id", "country_id", "date"]),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "countryiso3code", severity="warning"),
        c.check_accepted_values(df, s, "indicator_id", INDICATORS),
        c.check_accepted_values(df, s, "date", [WB_YEAR]),
        c.check_range(df, s, "value", 0),
        c.check_row_count(df, s, min_rows=500, max_rows=5_000),
        c.check_contains_values(df, s, "countryiso3code", ["PHL"]),
        c.check_contains_values(df, s, "indicator_id", INDICATORS),
    ]