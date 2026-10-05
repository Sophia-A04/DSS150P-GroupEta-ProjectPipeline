from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .clean_owid import build_staging_owid
from .clean_powerplants import build_staging_powerplants
from .clean_world_bank import build_staging_world_bank

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the staging layer from the raw layer.")
    parser.add_argument("--raw-dir", default=str(PROJECT_ROOT / "data" / "raw"))
    parser.add_argument("--staging-dir", default=str(PROJECT_ROOT / "data" / "staging"))
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    raw = Path(args.raw_dir)
    staging = Path(args.staging_dir)

    jobs = [
        ("powerplants", lambda: build_staging_powerplants(
            raw / "wri" / "global_power_plant_database.csv", staging / "stg_powerplants.parquet")),
        ("owid", lambda: build_staging_owid(
            raw / "owid" / "owid-co2-data.csv", staging / "stg_owid_2019.parquet")),
        ("world_bank", lambda: build_staging_world_bank(
            raw / "world_bank", staging / "stg_world_bank_2019.parquet")),
    ]

    failed = []
    for name, job in jobs:
        try:
            df = job()
            logger.info("Staging %s built: %d rows, %d columns", name, len(df), df.shape[1])
        except (FileNotFoundError, ValueError, KeyError) as exc:
            logger.error("Staging %s failed: %s", name, exc)
            failed.append(name)

    if failed:
        logger.error("Staging build FAILED for: %s", failed)
        return 1
    logger.info("Staging build completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())