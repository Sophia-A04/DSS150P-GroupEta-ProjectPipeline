import pandas as pd

from src.load.file_formats import benchmark


def sample(n=2_000):
    return pd.DataFrame({
        "country": ["PHL", "USA", "JPN", "IDN"] * (n // 4),
        "primary_fuel": ["Coal", "Gas", "Hydro", "Solar"] * (n // 4),
        "capacity_mw": [float(i % 300) + 0.5 for i in range(n)],
        "units": list(range(n)),
        "commissioned": pd.date_range("2000-01-01", periods=n, freq="D"),
        "active": [i % 2 == 0 for i in range(n)],
    })


def test_benchmark_covers_all_three_formats(tmp_path):
    rows = benchmark(sample(), tmp_path, repeats=1)
    assert [r["format"] for r in rows] == ["csv", "json", "parquet"]
    assert all(r["size_mb"] > 0 and r["rows_roundtrip"] == 2_000 for r in rows)


def test_parquet_preserves_schema_and_text_formats_do_not(tmp_path):
    rows = {r["format"]: r for r in benchmark(sample(), tmp_path, repeats=1)}
    assert rows["parquet"]["dtype_mismatches"] == 0
    assert rows["csv"]["dtype_mismatches"] >= 1
    assert "commissioned" in rows["csv"]["mismatched_columns"]


def test_parquet_is_smaller_than_json(tmp_path):
    rows = {r["format"]: r for r in benchmark(sample(), tmp_path, repeats=1)}
    assert rows["parquet"]["size_mb"] < rows["json"]["size_mb"]


def test_subset_defaults_to_first_columns_when_analytical_columns_absent(tmp_path):
    df = pd.DataFrame({"a": range(50), "b": range(50), "c": range(50), "d": range(50)})
    rows = benchmark(df, tmp_path, repeats=1)
    assert len(rows) == 3