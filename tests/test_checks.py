import pandas as pd

from src.validate import checks as c


def df():
    return pd.DataFrame({
        "id": ["A1", "A2", "A3"],
        "iso": ["PHL", "USA", "JPN"],
        "fuel": ["Coal", "Gas", "Hydro"],
        "x": [1.0, 2.0, 3.0],
        "name": ["a", "b", "c"],
    })


def test_schema_pass_and_fail():
    assert c.check_schema(df(), "t", ["id", "iso"]).passed
    r = c.check_schema(df(), "t", ["id", "missing_col"])
    assert not r.passed and r.check_type == "schema" and r.failed_count == 1


def test_dtypes_pass_and_fail():
    assert c.check_dtypes(df(), "t", {"x": "numeric", "id": "string"}).passed
    assert not c.check_dtypes(df(), "t", {"id": "numeric"}).passed
    assert not c.check_dtypes(df(), "t", {"x": "string"}).passed


def test_not_null_detects_null_and_blank():
    d = df()
    assert c.check_not_null(d, "t", ["id", "x"]).passed
    d.loc[0, "id"] = None
    d.loc[1, "name"] = "   "
    r = c.check_not_null(d, "t", ["id", "name"])
    assert not r.passed and r.failed_count == 2


def test_null_rate_threshold_and_default_severity():
    d = df()
    d.loc[[0, 1], "x"] = None
    r = c.check_null_rate(d, "t", "x", 0.5)
    assert not r.passed and r.severity == "warning"
    assert c.check_null_rate(d, "t", "x", 0.9).passed


def test_unique_single_and_composite():
    d = df()
    assert c.check_unique(d, "t", "id").passed
    d.loc[2, "id"] = "A1"
    assert not c.check_unique(d, "t", "id").passed
    assert c.check_unique(d, "t", ["id", "iso"]).passed


def test_duplicate_rows():
    d = pd.concat([df(), df().head(1)])
    r = c.check_duplicate_rows(d, "t")
    assert not r.passed and r.failed_count == 1


def test_accepted_values():
    assert c.check_accepted_values(df(), "t", "fuel", ["Coal", "Gas", "Hydro"]).passed
    r = c.check_accepted_values(df(), "t", "fuel", ["Coal"])
    assert not r.passed and r.failed_count == 2
    d = df()
    d.loc[0, "fuel"] = None
    assert c.check_accepted_values(d, "t", "fuel", ["Gas", "Hydro"], allow_null=True).passed
    assert not c.check_accepted_values(d, "t", "fuel", ["Gas", "Hydro"]).passed


def test_range_inclusive_exclusive_and_bounds():
    assert c.check_range(df(), "t", "x", 1, 3).passed
    assert not c.check_range(df(), "t", "x", 1, 2.5).passed
    assert not c.check_range(df(), "t", "x", 1, 3, inclusive_min=False).passed
    assert c.check_range(df(), "t", "x", min_value=0).passed


def test_iso3_format():
    assert c.check_iso3_format(df(), "t", "iso").passed
    d = df()
    d.loc[0, "iso"] = "ph"
    d.loc[1, "iso"] = "USAA"
    d.loc[2, "iso"] = None
    r = c.check_iso3_format(d, "t", "iso")
    assert not r.passed and r.failed_count == 3
    assert c.check_iso3_format(d.iloc[[2]], "t", "iso", allow_null=True).passed


def test_row_count_bounds():
    assert c.check_row_count(df(), "t", 1, 10).passed
    assert not c.check_row_count(df(), "t", 5).passed
    assert not c.check_row_count(df(), "t", 1, 2).passed


def test_row_count_preserved_with_tolerance():
    assert c.check_row_count_preserved(df(), "t", 3).passed
    assert not c.check_row_count_preserved(df(), "t", 4).passed
    assert c.check_row_count_preserved(df(), "t", 4, tolerance=0.5).passed


def test_contains_values():
    assert c.check_contains_values(df(), "t", "iso", ["PHL"]).passed
    r = c.check_contains_values(df(), "t", "iso", ["PHL", "XXX"])
    assert not r.passed and r.failed_count == 1


def test_referential_integrity():
    parent = pd.DataFrame({"iso": ["PHL", "USA", "JPN"]})
    child = pd.DataFrame({"country": ["PHL", "USA", "USA"]})
    assert c.check_referential_integrity(child, parent, "t", "country", "iso").passed
    child.loc[0, "country"] = "ZZZ"
    r = c.check_referential_integrity(child, parent, "t", "country", "iso")
    assert not r.passed and r.check_type == "referential_integrity" and r.failed_count == 1


def test_missing_column_is_reported_by_schema_check_only():
    assert c.check_range(df(), "t", "nope", 0, 1).passed
    assert c.check_unique(df(), "t", "nope").passed