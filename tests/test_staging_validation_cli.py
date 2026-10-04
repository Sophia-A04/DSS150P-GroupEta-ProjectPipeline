from src.validate.staging_validation import main
from tests.builders import build_staging_owid, build_staging_plants, build_staging_wb


def write(tmp_path, plants=None, owid=None, wb=None):
    paths = {}
    for key, df in {"plants": plants if plants is not None else build_staging_plants(),
                    "owid": owid if owid is not None else build_staging_owid(),
                    "world_bank": wb if wb is not None else build_staging_wb()}.items():
        p = tmp_path / f"{key}.csv"
        df.to_csv(p, index=False)
        paths[key] = str(p)
    return paths


def args(paths):
    return ["--plants", paths["plants"], "--owid", paths["owid"], "--world-bank", paths["world_bank"]]


def test_cli_passes_on_good_staging_tables(tmp_path):
    assert main(args(write(tmp_path))) == 0


def test_cli_fails_when_a_table_breaks_a_rule(tmp_path):
    wb = build_staging_wb()
    wb.loc[5, "iso_code"] = "PHL"
    assert main(args(write(tmp_path, wb=wb))) == 1


def test_cli_fails_when_a_file_is_missing(tmp_path):
    paths = write(tmp_path)
    paths["owid"] = str(tmp_path / "missing.csv")
    assert main(args(paths)) == 1