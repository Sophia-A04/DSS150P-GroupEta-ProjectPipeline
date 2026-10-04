from __future__ import annotations

import pandas as pd

from . import checks as c

SOURCE_NAME = "integrated_2019"

WB_COLS = ["wb_gdp_current_usd", "wb_population", "wb_gdp_per_capita_current_usd"]
FLAGS = ["owid_2019_matched", "wb_2019_matched"]
SHARE_COLS = ["country_primary_fuel_capacity_share_pct", "fossil_share_pct", "renewable_share_pct"]
REQUIRED_COLUMNS = [
    "country", "country_long", "name", "gppd_idnr", "capacity_mw", "primary_fuel",
    "latitude", "longitude", "total_installed_capacity_mw",
    "country_primary_fuel_capacity_mw", "country_primary_fuel_capacity_share_pct",
    "fossil_share_pct", "renewable_share_pct", "owid_country", "co2", "co2_per_capita",
] + WB_COLS + FLAGS


def _has(df, cols):
    return set(cols) <= set(df.columns)


def _phl(df):
    return df[df["country"] == "PHL"] if "country" in df.columns else df.iloc[0:0]


def _flag_mismatch(df, flag, ref):
    if not _has(df, ["country", flag]) or "iso_code" not in ref.columns:
        return 0
    in_ref = df["country"].isin(set(ref["iso_code"].dropna()))
    return int((df[flag].astype(bool) != in_ref).sum())


def _capacity_exceeds_totals(df):
    if not _has(df, ["capacity_mw", "total_installed_capacity_mw", "country_primary_fuel_capacity_mw"]):
        return 0
    over = ((df["capacity_mw"] > df["total_installed_capacity_mw"] + 1e-6)
            | (df["capacity_mw"] > df["country_primary_fuel_capacity_mw"] + 1e-6))
    return int(over.sum())


def validate(df: pd.DataFrame, expected_rows: int | None = None,
             owid: pd.DataFrame | None = None, wb: pd.DataFrame | None = None) -> list:
    s = SOURCE_NAME
    phl = _phl(df)
    phl_unmatched = int((~phl[FLAGS].astype(bool)).any(axis=1).sum()) if _has(phl, FLAGS) else 0
    phl_wb_missing = int(phl[WB_COLS].isna().any(axis=1).sum()) if _has(phl, WB_COLS) else 0
    share_overflow = 0
    if _has(df, ["fossil_share_pct", "renewable_share_pct"]):
        share_overflow = int(((df["fossil_share_pct"] + df["renewable_share_pct"]) > 100.01).sum())
    matched_null_wb = 0
    if _has(df, ["wb_2019_matched", "wb_gdp_current_usd"]):
        matched_null_wb = int((df["wb_2019_matched"].astype(bool) & df["wb_gdp_current_usd"].isna()).sum())

    results = [
        c.check_schema(df, s, REQUIRED_COLUMNS),
        c.check_dtypes(df, s, {"capacity_mw": "numeric", "co2": "numeric",
                               "wb_gdp_current_usd": "numeric", "wb_population": "numeric",
                               "wb_gdp_per_capita_current_usd": "numeric",
                               "country": "string", "gppd_idnr": "string"}),
        c.check_not_null(df, s, ["country", "gppd_idnr", "primary_fuel", "capacity_mw"]),
        c.check_unique(df, s, "gppd_idnr"),
        c.check_duplicate_rows(df, s),
        c.check_iso3_format(df, s, "country"),
        c.check_accepted_values(df, s, "owid_2019_matched", [True, False]),
        c.check_accepted_values(df, s, "wb_2019_matched", [True, False]),
        c.check_range(df, s, "capacity_mw", min_value=0, max_value=25000, inclusive_min=False),
        c.check_range(df, s, "co2", 0),
        c.check_range(df, s, "wb_population", 0),
        c.check_range(df, s, "wb_gdp_current_usd", 0),
        c.check_contains_values(df, s, "country", ["PHL"]),
        c.check_rule(s, "phl_rows_matched_to_sources", phl_unmatched,
                     f"{phl_unmatched} Philippine rows are not matched to OWID and World Bank"),
        c.check_rule(s, "phl_wb_values_populated", phl_wb_missing,
                     f"{phl_wb_missing} Philippine rows are missing World Bank values"),
        c.check_rule(s, "fossil_renewable_share_not_over_100", share_overflow,
                     f"{share_overflow} rows have fossil + renewable share above 100"),
        c.check_rule(s, "plant_capacity_within_country_totals", _capacity_exceeds_totals(df),
                     "plant capacity exceeds its country or country-fuel total"),
        c.check_rule(s, "wb_matched_rows_have_values", matched_null_wb,
                     f"{matched_null_wb} rows flagged as World Bank matched have no GDP value",
                     severity="warning"),
    ]
    for col in SHARE_COLS:
        results.append(c.check_range(df, s, col, 0, 100.01))

    if expected_rows is not None:
        results.append(c.check_row_count_preserved(df, s, expected_rows))
    else:
        results.append(c.check_row_count(df, s, min_rows=10_000, max_rows=100_000))

    if owid is not None:
        n = _flag_mismatch(df, "owid_2019_matched", owid)
        results.append(c.check_rule(s, "owid_match_flag_consistent", n,
                                    f"{n} rows where owid_2019_matched disagrees with staging OWID",
                                    check_type="referential_integrity"))
    if wb is not None:
        n = _flag_mismatch(df, "wb_2019_matched", wb)
        results.append(c.check_rule(s, "wb_match_flag_consistent", n,
                                    f"{n} rows where wb_2019_matched disagrees with staging World Bank",
                                    check_type="referential_integrity"))
    return results