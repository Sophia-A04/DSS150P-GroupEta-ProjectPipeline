from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import pandas as pd

from .checks import CheckResult, ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "outputs" / "validation_reports"
PROFILE_DIR = PROJECT_ROOT / "docs" / "profiling"

logger = logging.getLogger("validation")


def configure_logging(level=logging.INFO) -> None:
    if logger.handlers:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    for handler in (logging.StreamHandler(), logging.FileHandler(LOG_DIR / "validation.log", encoding="utf-8")):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(level)


def find_raw_files(suffix: str, keywords) -> List[Path]:
    found = []
    for p in RAW_DIR.rglob(f"*{suffix}"):
        if p.name.lower().endswith(".meta.json"):
            continue
        rel = p.relative_to(RAW_DIR).as_posix().lower()
        if any(k in rel for k in keywords):
            found.append(p)
    return sorted(found)


def finalize_report(results: List[CheckResult], source: str,
                    report_dir: Path = REPORT_DIR, raise_on_error: bool = True) -> dict:
    report_dir.mkdir(parents=True, exist_ok=True)
    for r in results:
        msg = "%s | %s | %s | failed=%d | %s"
        args = (source, r.check_type, r.check_name, r.failed_count, r.detail)
        if r.passed:
            logger.info("PASS | " + msg, *args)
        elif r.severity == "warning":
            logger.warning("WARN | " + msg, *args)
        else:
            logger.error("FAIL | " + msg, *args)

    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    summary = {
        "source": source,
        "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_checks": len(results),
        "passed": sum(r.passed for r in results),
        "errors": len(errors),
        "warnings": len(warnings),
        "status": "FAILED" if errors else "PASSED",
        "check_types": sorted({r.check_type for r in results}),
        "results": [r.to_dict() for r in results],
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (report_dir / f"{source}_validation_{stamp}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame([r.to_dict() for r in results]).to_csv(report_dir / f"{source}_validation_{stamp}.csv", index=False)

    logger.info("%s validation %s: %d checks, %d errors, %d warnings",
                source, summary["status"], len(results), len(errors), len(warnings))
    if errors and raise_on_error:
        raise ValidationError(f"{source}: {len(errors)} error-level check(s) failed: "
                              + ", ".join(r.check_name for r in errors))
    return summary