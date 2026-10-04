from src.validate.integration_validation import main
from tests.builders_integrated import build_integrated


def test_cli_passes_on_good_integrated_file(tmp_path):
    p = tmp_path / "integrated.csv"
    build_integrated().to_csv(p, index=False)
    assert main(["--path", str(p)]) == 0


def test_cli_fails_on_duplicate_plant_ids(tmp_path):
    df = build_integrated()
    df.loc[5, "gppd_idnr"] = df.loc[0, "gppd_idnr"]
    p = tmp_path / "integrated.csv"
    df.to_csv(p, index=False)
    assert main(["--path", str(p)]) == 1


def test_cli_fails_when_file_is_missing(tmp_path):
    assert main(["--path", str(tmp_path / "missing.csv")]) == 1