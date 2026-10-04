import pytest

from src.validate import owid_rules, world_bank_rules, wri_rules


def failed_errors(results):
    return {r.check_name for r in results if not r.passed and r.severity == "error"}


def test_wri_good_frame_has_no_errors(wri_df):
    assert failed_errors(wri_rules.validate(wri_df)) == set()


def test_owid_good_frame_has_no_errors(owid_df):
    assert failed_errors(owid_rules.validate(owid_df)) == set()


def test_world_bank_good_frame_has_no_errors(wb_df):
    assert failed_errors(world_bank_rules.validate(wb_df)) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["capacity_mw"]), "required_columns_present"),
    (lambda d: d.assign(name=d["name"].where(d.index != 5, None)), "required_fields_not_null"),
    (lambda d: d.assign(gppd_idnr=d["gppd_idnr"].where(d.index != 5, "GPPD0000000")), "unique_gppd_idnr"),
    (lambda d: d.assign(country=d["country"].where(d.index != 5, "us")), "country_iso3_format"),
    (lambda d: d.assign(primary_fuel=d["primary_fuel"].where(d.index != 5, "Unobtainium")), "primary_fuel_accepted_values"),
    (lambda d: d.assign(capacity_mw=d["capacity_mw"].where(d.index != 5, 0.0)), "capacity_mw_range"),
    (lambda d: d.assign(latitude=d["latitude"].where(d.index != 5, 123.0)), "latitude_range"),
    (lambda d: d.assign(longitude=d["longitude"].where(d.index != 5, -200.0)), "longitude_range"),
    (lambda d: d.assign(country=d["country"].replace("PHL", "USA")), "country_contains_required"),
    (lambda d: d.head(100), "row_count_sanity"),
    (lambda d: d.assign(capacity_mw=d["capacity_mw"].astype(str)), "expected_dtypes"),
])
def test_wri_failure_is_detected(wri_df, mutate, expected):
    assert expected in failed_errors(wri_rules.validate(mutate(wri_df)))


def test_wri_negative_generation_is_warning_only(wri_df):
    wri_df.loc[3, "generation_gwh_2019"] = -10.0
    results = wri_rules.validate(wri_df)
    flagged = [r for r in results if r.check_name == "generation_gwh_2019_range"][0]
    assert not flagged.passed and flagged.severity == "warning"
    assert failed_errors(results) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["co2"]), "required_columns_present"),
    (lambda d: d.assign(year=d["year"].where(d.index != 5, 1200)), "year_range"),
    (lambda d: d.assign(co2=d["co2"].where(d.index != 5, -5.0)), "co2_range"),
    (lambda d: d.assign(iso_code=d["iso_code"].where(d.index != 5, "XX")), "iso_code_iso3_format"),
    (lambda d: d.assign(share_global_co2=d["share_global_co2"].where(d.index != 5, 140.0)), "share_global_co2_range"),
    (lambda d: __import__("pandas").concat([d, d.head(2)], ignore_index=True), "unique_country+year"),
    (lambda d: d.assign(iso_code=d["iso_code"].replace("PHL", "AAX")), "iso_code_contains_required"),
    (lambda d: d[d["year"] != 2019], "year_contains_required"),
])
def test_owid_failure_is_detected(owid_df, mutate, expected):
    assert expected in failed_errors(owid_rules.validate(mutate(owid_df)))


def test_owid_null_iso_for_aggregates_is_allowed(owid_df):
    owid_df.loc[owid_df["country"] == "Country 5", "iso_code"] = None
    assert failed_errors(owid_rules.validate(owid_df)) == set()


@pytest.mark.parametrize("mutate, expected", [
    (lambda d: d.drop(columns=["value"]), "required_columns_present"),
    (lambda d: d.assign(indicator_id=d["indicator_id"].where(d.index != 5, "BAD.CODE")), "indicator_id_accepted_values"),
    (lambda d: d.assign(date=d["date"].where(d.index != 5, "2018")), "date_accepted_values"),
    (lambda d: d.assign(value=d["value"].where(d.index != 5, -1.0)), "value_range"),
    (lambda d: d[d["countryiso3code"] != "PHL"], "countryiso3code_contains_required"),
    (lambda d: d[d["indicator_id"] != "SP.POP.TOTL"], "indicator_id_contains_required"),
    (lambda d: d.head(50), "row_count_sanity"),
])
def test_world_bank_failure_is_detected(wb_df, mutate, expected):
    assert expected in failed_errors(world_bank_rules.validate(mutate(wb_df)))


def test_world_bank_blank_iso_is_warning_only(wb_df):
    wb_df.loc[7, "countryiso3code"] = ""
    results = world_bank_rules.validate(wb_df)
    flagged = [r for r in results if r.check_name == "countryiso3code_iso3_format"][0]
    assert not flagged.passed and flagged.severity == "warning"
    assert failed_errors(results) == set()