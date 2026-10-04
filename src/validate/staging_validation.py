from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import staging_rules as rules
from .checks import ValidationError
from .reporting import PROJECT_ROOT, configure_logging, finalize_report, logger

STAGING_DIR = PROJECT_ROOT / "data" / "staging"
TABLES = {
    "plants": (rules.PLANTS, ("plant", "gppd", "wri")),
    "owid": (rules.OWID, ("owid", "co2")),
    "world-bank": (rules.WB, ("world_bank", "worldbank", "wb_")),
}


def find_table(keywords) -> Path | None:
    files = sorted(p for p in STAGING_DIR.rglob("*")
                   if p.suffix.lower() in (".csv", ".parquet")
                   and any(k in p.name.lower() for k in keywords))
    return files[0] if files else None


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def raw_plant_count() -> int | None:
    from .wri_rules import load, locate
    paths = locate()
    return len(load(paths)) if paths else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate staging-layer tables.")
    parser.add_argument("--plants", default=None)
    parser.add_argument("--owid", default=None)
    parser.add_argument("--world-bank", dest="world_bank", default=None)
    args = parser.parse_args(argv)

    configure_logging()
    frames, failed = {}, []
    for key, (name, keywords) in TABLES.items():
        override = getattr(args, key.replace("-", "_"))
        try:
            path = Path(override) if override else find_table(keywords)
            if path is None or not path.exists():
                raise FileNotFoundError(f"No staging table found for '{key}' "
                                        f"(looked in {STAGING_DIR}); pass --{key} to override.")
            logger.info("Loading %s from %s", key, path)
            df = read_table(path)
            frames[key] = df
            if key == "plants":
                raw_count = None if override else raw_plant_count()
                results = rules.validate_plants(df, raw_count)
            elif key == "owid":
                results = rules.validate_owid(df)
            else:
                results = rules.validate_world_bank(df)
            finalize_report(results, name)
        except (FileNotFoundError, ValueError, ValidationError, ImportError) as exc:
            logger.error("Staging table '%s' did not pass: %s", key, exc)
            failed.append(key)

    if len(frames) == len(TABLES):
        finalize_report(rules.validate_cross_table(frames["plants"], frames["owid"],
                                                   frames["world-bank"]),
                        rules.CROSS, raise_on_error=False)
    if failed:
        logger.error("Staging validation FAILED for: %s", failed)
        return 1
    logger.info("Staging validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())