import json

import pytest

from src.validate import owid_rules, reporting, world_bank_rules, wri_rules


@pytest.fixture
def raw_tree(tmp_path, monkeypatch):
    for rel in ["wri/global_power_plant_database.csv", "owid/owid-co2-data.csv",
                "world_bank/gdp_per_capita.json", "world_bank/population.json",
                "world_bank/gdp_per_capita.json.meta.json", "wri/global_power_plant_database.csv.meta.json"]:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps([]) if rel.endswith("json") else "a,b\n1,2\n")
    monkeypatch.setattr(reporting, "RAW_DIR", tmp_path)
    return tmp_path


def test_wri_file_is_found_in_subfolder(raw_tree):
    assert [p.name for p in wri_rules.locate()] == ["global_power_plant_database.csv"]


def test_owid_file_is_found_in_subfolder(raw_tree):
    assert [p.name for p in owid_rules.locate()] == ["owid-co2-data.csv"]


def test_world_bank_files_found_by_folder_and_metadata_sidecars_skipped(raw_tree):
    names = sorted(p.name for p in world_bank_rules.locate())
    assert names == ["gdp_per_capita.json", "population.json"]