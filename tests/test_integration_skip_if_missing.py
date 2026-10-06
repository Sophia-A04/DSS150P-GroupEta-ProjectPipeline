from src.validate import integration_validation
from src.validate.integration_validation import main
from tests.builders_integrated import build_integrated


def test_missing_dataset_skips_with_code_99_when_flag_is_set(monkeypatch, tmp_path):
    monkeypatch.setattr(integration_validation, "CURATED_DIR", tmp_path)
    assert main(["--skip-if-missing"]) == 99


def test_missing_dataset_still_fails_without_the_flag(monkeypatch, tmp_path):
    monkeypatch.setattr(integration_validation, "CURATED_DIR", tmp_path)
    assert main([]) == 1


def test_explicit_missing_path_fails_even_with_the_flag(tmp_path):
    assert main(["--path", str(tmp_path / "missing.csv"), "--skip-if-missing"]) == 1


def test_existing_dataset_is_validated_normally_with_the_flag(monkeypatch, tmp_path):
    monkeypatch.setattr(integration_validation, "CURATED_DIR", tmp_path)
    build_integrated().to_csv(tmp_path / "integrated_plants.csv", index=False)
    assert main(["--skip-if-missing", "--path", str(tmp_path / "integrated_plants.csv")]) == 0