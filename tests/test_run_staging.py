import logging

from src.transform import run_staging


def patch(monkeypatch, tmp_path, calls, fail=None):
    monkeypatch.setattr(run_staging, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(run_staging, "STAGING_DIR", tmp_path / "stg")
    for name in ["build_staging_powerplants", "build_staging_owid", "build_staging_world_bank"]:
        def make(n):
            def build(**kwargs):
                if n == fail:
                    raise FileNotFoundError("raw file missing")
                calls.append((n, kwargs))
            return build
        monkeypatch.setattr(run_staging, name, make(name))


def test_all_three_builders_run_and_staging_dir_is_created(monkeypatch, tmp_path):
    calls = []
    patch(monkeypatch, tmp_path, calls)
    assert run_staging.main() == 0
    assert [c[0] for c in calls] == ["build_staging_powerplants", "build_staging_owid", "build_staging_world_bank"]
    outputs = [str(c[1]["output_path"]).replace("\\", "/") for c in calls]
    assert [o.rsplit("/", 1)[1] for o in outputs] == ["powerplants.parquet", "owid.parquet", "world_bank.parquet"]
    assert (tmp_path / "stg").is_dir()


def test_failed_source_returns_nonzero_and_other_builders_still_run(monkeypatch, tmp_path):
    calls = []
    patch(monkeypatch, tmp_path, calls, fail="build_staging_owid")
    assert run_staging.main() == 1
    assert [c[0] for c in calls] == ["build_staging_powerplants", "build_staging_world_bank"]


def test_failure_is_logged_with_source_name(monkeypatch, tmp_path, caplog):
    patch(monkeypatch, tmp_path, [], fail="build_staging_world_bank")
    caplog.set_level(logging.ERROR)
    run_staging.main()
    assert any("world_bank" in r.getMessage() for r in caplog.records)