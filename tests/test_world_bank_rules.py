import pandas as pd
import pytest

from src.validate import world_bank_rules as rules


def failed_errors(results):
    return {r.check_name for r in results if not r.passed and r.severity == "error"}


def test_good_frame_has_no_errors(wb_df):
    assert failed_errors(rules.validate(wb_df)) == set()


def test_multi_year_history_is_accepted(wb_df):
    older = wb_df.assign(date="2018", country_id=wb_df["country_id"] + "_old")
    both = pd.concat([wb_df, older], ignore_index=True)
    assert failed_errors(rules.validate(both)) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["value"]), "required_columns_present"),
    (lambda d: d.assign(indicator_id=d["indicator_id"].where(d.index != 5, "BAD.CODE")), "indicator_id_accepted_values"),
    (lambda d: d.assign(date="1800"), "date_year_range"),
    (lambda d: d.assign(date="2018"), "date_contains_required"),
    (lambda d: d.assign(value=d["value"].where(d.index != 5, -1.0)), "value_range"),
    (lambda d: d[d["countryiso3code"] != "PHL"], "countryiso3code_contains_required"),
    (lambda d: d[d["indicator_id"] != "SP.POP.TOTL"], "indicator_id_contains_required"),
    (lambda d: d.head(50), "row_count_sanity"),
    (lambda d: pd.concat([d, d.head(2)], ignore_index=True), "unique_indicator_id+country_id+date"),
])
def test_failure_is_detected(wb_df, mutate, expected):
    assert expected in failed_errors(rules.validate(mutate(wb_df)))


def test_blank_iso_is_warning_only(wb_df):
    wb_df.loc[7, "countryiso3code"] = ""
    results = rules.validate(wb_df)
    flagged = [r for r in results if r.check_name == "countryiso3code_iso3_format"][0]
    assert not flagged.passed and flagged.severity == "warning"
    assert failed_errors(results) == set()


def test_missing_total_gdp_indicator_is_warning_only(wb_df):
    df = wb_df[wb_df["indicator_id"] != "NY.GDP.MKTP.CD"]
    df = pd.concat([df, df.assign(date="2018", country_id=df["country_id"] + "_x")], ignore_index=True)
    results = rules.validate(df)
    flagged = [r for r in results if r.check_name == "indicator_id_contains_required"
               and r.severity == "warning"]
    assert flagged and not flagged[0].passed
    assert failed_errors(results) == set()


def test_truncated_api_response_is_detected(wb_df):
    wb_df["source_file"] = "gdp_per_capita.json"
    wb_df["_meta_total"] = len(wb_df) + 100
    assert "api_response_complete" in failed_errors(rules.validate(wb_df))


def test_complete_api_response_passes(wb_df):
    wb_df["source_file"] = "gdp_per_capita.json"
    wb_df["_meta_total"] = len(wb_df)
    assert "api_response_complete" not in failed_errors(rules.validate(wb_df))