from src.transform import run_curated


def test_run_curated_calls_builder(
    monkeypatch,
    tmp_path,
):
    staging_dir = tmp_path / "staging"
    curated_dir = tmp_path / "curated"

    staging_dir.mkdir()

    monkeypatch.setattr(
        run_curated,
        "STAGING_DIR",
        staging_dir,
    )

    monkeypatch.setattr(
        run_curated,
        "CURATED_DIR",
        curated_dir,
    )

    calls = {}

    class FakeFrame:
        def __len__(self):
            return 10

        def __getitem__(
            self,
            key,
        ):
            assert key == "gppd_idnr"

            class FakeSeries:
                def nunique(self):
                    return 10

            return FakeSeries()

    def fake_builder(**kwargs):
        calls.update(kwargs)
        return FakeFrame()

    monkeypatch.setattr(
        run_curated,
        "build_curated_dataset",
        fake_builder,
    )

    assert run_curated.main() == 0

    assert calls["plants_path"] == (
        staging_dir
        / "powerplants.parquet"
    )

    assert calls["owid_path"] == (
        staging_dir
        / "owid.parquet"
    )

    assert calls["world_bank_path"] == (
        staging_dir
        / "world_bank.parquet"
    )

    assert calls["output_path"] == (
        curated_dir
        / "eta_curated_2019.parquet"
    )


def test_run_curated_returns_nonzero_on_failure(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        run_curated,
        "STAGING_DIR",
        tmp_path / "staging",
    )

    monkeypatch.setattr(
        run_curated,
        "CURATED_DIR",
        tmp_path / "curated",
    )

    def fail_builder(**kwargs):
        raise FileNotFoundError(
            "staging file missing"
        )

    monkeypatch.setattr(
        run_curated,
        "build_curated_dataset",
        fail_builder,
    )

    assert run_curated.main() == 1