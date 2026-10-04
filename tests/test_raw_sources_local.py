import importlib

import pytest

from src.validate.raw_validation import SOURCES


@pytest.mark.parametrize("key", list(SOURCES))
def test_real_raw_source_has_no_error_level_failures(key):
    module = importlib.import_module(SOURCES[key])
    paths = module.locate()
    if not paths:
        pytest.skip(f"No raw file for '{key}' in data/raw")
    results = module.validate(module.load(paths))
    errors = [r.check_name for r in results if not r.passed and r.severity == "error"]
    assert errors == []