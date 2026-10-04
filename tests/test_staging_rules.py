import pandas as pd
import pytest

from src.validate import checks as c
from src.validate import staging_rules as rules
from tests.builders import build_staging_owid, build_staging_plants, build_staging_wb


def failed_errors(results):
    return {r.check_name for r in results if not r.passed and r.severity == "error"}


def test_good_plants_has_no_errors():
    assert failed_errors(rules.validate_plants(build_staging_plants(), raw_row_count=10_000)) == set()


def test_good_owid_has_no_errors():
    assert failed_errors(rules.validate_owid(build_staging_owid())) == set()


def test_good_world_bank_has_no_errors():
    assert failed_errors(rules.validate_world_bank(build_staging_wb())) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["capacity_mw"]), "required_columns_present"),
    (lambda d: d.assign(gppd_idnr=d["gppd_idnr"].where(d.index != 5, "GPPD0000000")), "unique_gppd_idnr"),
    (lambda d: d.assign(capacity_mw=d["capacity_mw"].where(d.index != 5, 0.0)), "capacity_mw_range"),
    (lambda d: d.assign(capacity_mw=d["capacity_mw"].where(d.index != 5, None)), "required_fields_not_null"),
    (lambda d: d.assign(country=d["country"].where(d.index != 5, " usa")), "country_iso3_format"),
    (lambda d: d.assign(primary_fuel=d["primary_fuel"].where(d.index != 5, "Unknown")), "primary_fuel_accepted_values"),
    (lambda d: d.assign(country=d["country"].replace("PHL", "USA")), "country_contains_required"),
    (lambda d: d.head(500), "row_count_sanity"),
])
def test_plants_failure_is_detected(mutate, expected):
    assert expected in failed_errors(rules.validate_plants(mutate(build_staging_plants())))


def test_plants_row_loss_versus_raw_is_detected():
    results = rules.validate_plants(build_staging_plants(10_000), raw_row_count=12_000)
    assert "row_count_preserved" in failed_errors(results)


def test_plants_small_row_loss_within_tolerance_is_allowed():
    results = rules.validate_plants(build_staging_plants(10_000), raw_row_count=10_200)
    assert "row_count_preserved" not in failed_errors(results)


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["co2"]), "required_columns_present"),
    (lambda d: d.assign(population=1.0), "forbidden_columns_absent"),
    (lambda d: d.assign(gdp=1.0), "forbidden_columns_absent"),
    (lambda d: d.assign(year=d["year"].where(d.index != 5, 2018)), "year_accepted_values"),
    (lambda d: d.assign(iso_code=d["iso_code"].where(d.index != 5, "PHL")), "unique_iso_code"),
    (lambda d: d.assign(iso_code=d["iso_code"].where(d.index != 5, None)), "required_fields_not_null"),
    (lambda d: d.assign(co2=d["co2"].where(d.index != 5, -1.0)), "co2_range"),
    (lambda d: d[d["iso_code"] != "PHL"], "iso_code_contains_required"),
    (lambda d: d.head(20), "row_count_sanity"),
])
def test_owid_failure_is_detected(mutate, expected):
    assert expected in failed_errors(rules.validate_owid(mutate(build_staging_owid())))


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["wb_population"]), "required_columns_present"),
    (lambda d: d.assign(iso_code=d["iso_code"].where(d.index != 5, "PHL")), "unique_iso_code"),
    (lambda d: d.assign(wb_year=d["wb_year"].where(d.index != 5, "2018")), "wb_year_accepted_values"),
    (lambda d: d.assign(wb_gdp_current_usd=d["wb_gdp_current_usd"].where(d.index != 5, -1.0)), "wb_gdp_current_usd_range"),
    (lambda d: d.assign(wb_population=d["wb_population"].where(d.index != 0, None)), "phl_indicator_values_populated"),
    (lambda d: d[d["iso_code"] != "PHL"], "iso_code_contains_required"),
    (lambda d: d.head(20), "row_count_sanity"),
])
def test_world_bank_failure_is_detected(mutate, expected):
    assert expected in failed_errors(rules.validate_world_bank(mutate(build_staging_wb())))


def test_world_bank_null_for_other_countries_is_allowed():
    wb = build_staging_wb()
    wb.loc[10, "wb_gdp_current_usd"] = None
    assert failed_errors(rules.validate_world_bank(wb)) == set()


def test_cross_table_flags_unmatched_countries_as_warnings_only():
    plants = build_staging_plants()
    plants.loc[7, "country"] = "ZZZ"
    results = rules.validate_cross_table(plants, build_staging_owid(), build_staging_wb())
    assert all(r.severity == "warning" for r in results)
    assert not all(r.passed for r in results)
    assert failed_errors(results) == set()


def test_columns_absent_and_rule_helpers():
    df = pd.DataFrame({"a": [1]})
    assert c.check_columns_absent(df, "t", ["b"]).passed
    assert not c.check_columns_absent(df, "t", ["a"]).passed
    assert c.check_rule("t", "r", 0, "x").passed
    assert not c.check_rule("t", "r", 2, "x").passed