import json
import logging

import pytest

from src.validate import checks as c
from src.validate.raw_validation import main
from src.validate.reporting import finalize_report


def passing():
    return c.CheckResult("t", "schema", "ok_check", True, "error", 0, "OK")


def failing(severity="error"):
    return c.CheckResult("t", "range", "bad_check", False, severity, 3, "3 bad values")


def test_passing_run_writes_json_and_csv_reports(tmp_path):
    summary = finalize_report([passing()], "t", report_dir=tmp_path)
    assert summary["status"] == "PASSED"
    assert len(list(tmp_path.glob("t_validation_*.json"))) == 1
    assert len(list(tmp_path.glob("t_validation_*.csv"))) == 1


def test_error_failure_raises_but_still_writes_report(tmp_path):
    with pytest.raises(c.ValidationError, match="bad_check"):
        finalize_report([passing(), failing()], "t", report_dir=tmp_path)
    report = json.loads(next(tmp_path.glob("t_validation_*.json")).read_text())
    assert report["status"] == "FAILED" and report["errors"] == 1


def test_warning_does_not_raise(tmp_path):
    summary = finalize_report([passing(), failing("warning")], "t", report_dir=tmp_path)
    assert summary["status"] == "PASSED" and summary["warnings"] == 1


def test_failures_are_logged(tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="validation")
    with pytest.raises(c.ValidationError):
        finalize_report([failing()], "t", report_dir=tmp_path)
    assert any(r.levelno == logging.ERROR and "bad_check" in r.getMessage() for r in caplog.records)


def test_cli_returns_nonzero_for_missing_file():
    assert main(["--source", "wri", "--path", "does_not_exist.csv"]) == 1