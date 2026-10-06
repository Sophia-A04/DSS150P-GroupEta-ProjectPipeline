from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import integration_rules as rules
from .checks import ValidationError
from .reporting import PROJECT_ROOT, configure_logging, finalize_report, logger
from .staging_validation import find_table, read_table

CURATED_DIR = PROJECT_ROOT / "data" / "curated"
KEYWORDS = ("merged", "integrated", "curated", "plant")


def find_curated() -> Path | None:
    files = sorted(p for p in CURATED_DIR.rglob("*")
                   if p.suffix.lower() in (".csv", ".parquet")
                   and any(k in p.name.lower() for k in KEYWORDS))
    return files[0] if files else None


def load_staging_context():
    plants = find_table(("plant", "gppd", "wri"))
    owid = find_table(("owid", "co2"))
    wb = find_table(("world_bank", "worldbank", "wb_"))
    return (len(read_table(plants)) if plants else None,
            read_table(owid) if owid else None,
            read_table(wb) if wb else None)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate the integrated plant-level dataset.")
    parser.add_argument("--path", default=None, help="Integrated dataset (csv or parquet)")
    parser.add_argument("--skip-if-missing", action="store_true",
                        help="Exit with code 99 (Airflow skip) when no dataset is found in data/curated")
    args = parser.parse_args(argv)

    configure_logging()
    try:
        path = Path(args.path) if args.path else find_curated()
        if path is None and args.skip_if_missing:
            logger.warning("No integrated dataset found in %s; skipping validation (exit code 99).", CURATED_DIR)
            return 99
        if path is None or not path.exists():
            raise FileNotFoundError(f"No integrated dataset found (looked in {CURATED_DIR}); "
                                    f"pass --path to override.")
        logger.info("Loading integrated dataset from %s", path)
        df = read_table(path)
        expected_rows, owid, wb = (None, None, None) if args.path else load_staging_context()
        finalize_report(rules.validate(df, expected_rows, owid, wb), rules.SOURCE_NAME)
    except (FileNotFoundError, ValueError, ValidationError, ImportError) as exc:
        logger.error("Integrated validation did not pass: %s", exc)
        return 1
    logger.info("Integrated validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())