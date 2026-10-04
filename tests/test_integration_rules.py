import pandas as pd
import pytest

from src.validate import integration_rules as rules
from tests.builders import build_staging_owid, build_staging_wb
from tests.builders_integrated import build_integrated


def failed_errors(results):
    return {r.check_name for r in results if not r.passed and r.severity == "error"}


def setcell(d, col, value, row=5):
    d = d.copy()
    d[col] = d[col].astype(object)
    d.loc[row, col] = value
    return d


def test_good_integrated_frame_has_no_errors():
    results = rules.validate(build_integrated(), expected_rows=10_000,
                             owid=build_staging_owid(), wb=build_staging_wb())
    assert failed_errors(results) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["wb_population"]), "required_columns_present"),
    (lambda d: setcell(d, "gppd_idnr", "GPPD0000000"), "unique_gppd_idnr"),
    (lambda d: pd.concat([d, d.head(2)], ignore_index=True), "no_fully_duplicated_rows"),
    (lambda d: setcell(d, "country", "us"), "country_iso3_format"),
    (lambda d: setcell(d, "capacity_mw", 0.0), "capacity_mw_range"),
    (lambda d: setcell(d, "capacity_mw", None), "required_fields_not_null"),
    (lambda d: setcell(d, "fossil_share_pct", 150.0), "fossil_share_pct_range"),
    (lambda d: setcell(d, "fossil_share_pct", 70.0), "fossil_renewable_share_not_over_100"),
    (lambda d: d.assign(country=d["country"].replace("PHL", "USA")), "country_contains_required"),
    (lambda d: setcell(d, "owid_2019_matched", False, row=0), "phl_rows_matched_to_sources"),
    (lambda d: setcell(d, "wb_population", None, row=0), "phl_wb_values_populated"),
    (lambda d: setcell(d, "capacity_mw", 10_000_000.0), "plant_capacity_within_country_totals"),
    (lambda d: setcell(d, "owid_2019_matched", "maybe"), "owid_2019_matched_accepted_values"),
    (lambda d: setcell(d, "wb_population", -5.0), "wb_population_range"),
    (lambda d: d.head(100), "row_count_sanity"),
])
def test_integrated_failure_is_detected(mutate, expected):
    assert expected in failed_errors(rules.validate(mutate(build_integrated())))


def test_grain_loss_versus_staging_is_detected():
    results = rules.validate(build_integrated().head(9_000), expected_rows=10_000)
    assert "row_count_preserved" in failed_errors(results)


def test_grain_gain_versus_staging_is_detected():
    df = build_integrated()
    results = rules.validate(pd.concat([df, df.head(5)], ignore_index=True), expected_rows=10_000)
    assert "row_count_preserved" in failed_errors(results)


def test_match_flag_disagreeing_with_staging_is_detected():
    df = setcell(build_integrated(), "country", "ZZZ")
    results = rules.validate(df, owid=build_staging_owid(), wb=build_staging_wb())
    errors = failed_errors(results)
    assert "owid_match_flag_consistent" in errors and "wb_match_flag_consistent" in errors


def test_unmatched_country_flagged_false_is_consistent():
    df = setcell(build_integrated(), "country", "ZZZ")
    df = setcell(df, "owid_2019_matched", False)
    df = setcell(df, "wb_2019_matched", False)
    results = rules.validate(df, owid=build_staging_owid(), wb=build_staging_wb())
    assert "owid_match_flag_consistent" not in failed_errors(results)
    assert "wb_match_flag_consistent" not in failed_errors(results)


def test_matched_row_without_wb_value_is_warning_only():
    df = build_integrated()
    df.loc[100, "wb_gdp_current_usd"] = None
    results = rules.validate(df)
    flagged = [r for r in results if r.check_name == "wb_matched_rows_have_values"][0]
    assert not flagged.passed and flagged.severity == "warning"
    assert failed_errors(results) == set()