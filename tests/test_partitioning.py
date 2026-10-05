import pandas as pd
import pytest

from src.load.partitioning import (count_fragments, read_partitions, timed_comparison,
                                   write_partitioned)


def sample():
    countries = ["PHL"] * 5 + ["USA"] * 20 + ["JPN"] * 10 + ["IDN"] * 7
    return pd.DataFrame({
        "country": countries,
        "gppd_idnr": [f"G{i:04d}" for i in range(len(countries))],
        "capacity_mw": [float(i + 1) for i in range(len(countries))],
    })


def test_one_directory_per_country(tmp_path):
    summary = write_partitioned(sample(), tmp_path / "p", "country")
    dirs = sorted(d.name for d in (tmp_path / "p").iterdir() if d.is_dir())
    assert dirs == ["country=IDN", "country=JPN", "country=PHL", "country=USA"]
    assert summary["partitions"] == 4 and summary["rows"] == 42
    assert summary["largest"] == ("USA", 20) and summary["smallest"] == ("PHL", 5)


def test_selected_partition_returns_exact_rows(tmp_path):
    df = sample()
    write_partitioned(df, tmp_path / "p", "country")
    out = read_partitions(tmp_path / "p", "country", ["PHL"])
    expected = df[df["country"] == "PHL"]
    assert len(out) == 5
    assert set(out["gppd_idnr"]) == set(expected["gppd_idnr"])
    assert set(out["country"]) == {"PHL"}


def test_only_selected_partition_files_are_touched(tmp_path):
    write_partitioned(sample(), tmp_path / "p", "country")
    selected, total = count_fragments(tmp_path / "p", "country", ["PHL"])
    assert (selected, total) == (1, 4)
    selected, total = count_fragments(tmp_path / "p", "country", ["PHL", "JPN"])
    assert (selected, total) == (2, 4)


def test_multiple_partitions_can_be_read_together(tmp_path):
    write_partitioned(sample(), tmp_path / "p", "country")
    out = read_partitions(tmp_path / "p", "country", ["PHL", "IDN"], columns=["country", "capacity_mw"])
    assert len(out) == 12 and list(out.columns) == ["country", "capacity_mw"]


def test_rerun_does_not_duplicate_rows(tmp_path):
    df = sample()
    write_partitioned(df, tmp_path / "p", "country")
    write_partitioned(df, tmp_path / "p", "country")
    assert len(read_partitions(tmp_path / "p", "country", ["PHL", "USA", "JPN", "IDN"])) == 42


def test_null_partition_key_is_rejected(tmp_path):
    df = sample()
    df.loc[0, "country"] = None
    with pytest.raises(ValueError, match="nulls"):
        write_partitioned(df, tmp_path / "p", "country")


def test_missing_partition_key_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="not a column"):
        write_partitioned(sample(), tmp_path / "p", "region")


def test_timed_comparison_returns_matching_row_counts(tmp_path):
    df = sample()
    write_partitioned(df, tmp_path / "p", "country")
    stats = timed_comparison(lambda: df, tmp_path / "p", "country", ["PHL"], repeats=1)
    assert stats["rows_full_scan"] == stats["rows_partition_read"] == 5
    assert stats["fragments_read"] == 1 and stats["fragments_total"] == 4