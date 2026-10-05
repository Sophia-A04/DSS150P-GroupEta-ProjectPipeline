import pandas as pd

from src.transform import build_staging


def fake_builder(calls, name):
    def build(*args, **kwargs):
        calls.append((name, [str(a) for a in args]))
        return pd.DataFrame({"a": [1, 2, 3]})
    return build


def patch_all(monkeypatch, calls):
    monkeypatch.setattr(build_staging, "build_staging_powerplants", fake_builder(calls, "powerplants"))
    monkeypatch.setattr(build_staging, "build_staging_owid", fake_builder(calls, "owid"))
    monkeypatch.setattr(build_staging, "build_staging_world_bank", fake_builder(calls, "world_bank"))


def test_all_three_builders_run_with_expected_paths(monkeypatch, tmp_path):
    calls = []
    patch_all(monkeypatch, calls)
    code = build_staging.main(["--raw-dir", str(tmp_path / "raw"), "--staging-dir", str(tmp_path / "stg")])
    assert code == 0
    assert [c[0] for c in calls] == ["powerplants", "owid", "world_bank"]
    joined = {c[0]: " ".join(c[1]).replace("\\", "/") for c in calls}
    assert "raw/wri/global_power_plant_database.csv" in joined["powerplants"]
    assert "stg/stg_powerplants.parquet" in joined["powerplants"]
    assert "raw/owid/owid-co2-data.csv" in joined["owid"]
    assert "stg/stg_owid_2019.parquet" in joined["owid"]
    assert "raw/world_bank" in joined["world_bank"]
    assert "stg/stg_world_bank_2019.parquet" in joined["world_bank"]


def test_missing_raw_file_returns_nonzero_and_other_builders_still_run(monkeypatch, tmp_path):
    calls = []
    patch_all(monkeypatch, calls)

    def missing(*args, **kwargs):
        raise FileNotFoundError("OWID raw dataset not found")

    monkeypatch.setattr(build_staging, "build_staging_owid", missing)
    code = build_staging.main(["--raw-dir", str(tmp_path), "--staging-dir", str(tmp_path)])
    assert code == 1
    assert [c[0] for c in calls] == ["powerplants", "world_bank"]


def test_failure_is_logged(monkeypatch, tmp_path, caplog):
    patch_all(monkeypatch, [])

    def bad(*args, **kwargs):
        raise ValueError("bad payload")

    monkeypatch.setattr(build_staging, "build_staging_world_bank", bad)
    build_staging.main(["--raw-dir", str(tmp_path), "--staging-dir", str(tmp_path)])
    assert any("world_bank failed" in r.getMessage() for r in caplog.records)