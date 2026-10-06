"""
Orchestrator for the staging layer.

Reads all three raw source files and writes the staging Parquet outputs
by delegating to the per-source transformation modules.

Usage:
    python -m src.transform.run_staging
"""
import logging
import sys
from pathlib import Path

from src.transform.clean_powerplants import build_staging_powerplants
from src.transform.clean_owid import build_staging_owid
from src.transform.clean_world_bank import build_staging_world_bank

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
STAGING_DIR = PROJECT_ROOT / "data" / "staging"


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    # --- WRI power plants ---
    try:
        logger.info("Building staging: powerplants")
        build_staging_powerplants(
            raw_path=RAW_DIR / "wri" / "global_power_plant_database.csv",
            output_path=STAGING_DIR / "powerplants.parquet",
        )
        results["powerplants"] = True
    except Exception:
        logger.exception("Failed to build powerplants staging")
        results["powerplants"] = False

    # --- OWID CO2 ---
    try:
        logger.info("Building staging: owid")
        build_staging_owid(
            raw_path=RAW_DIR / "owid" / "owid-co2-data.csv",
            output_path=STAGING_DIR / "owid.parquet",
        )
        results["owid"] = True
    except Exception:
        logger.exception("Failed to build owid staging")
        results["owid"] = False

    # --- World Bank ---
    try:
        logger.info("Building staging: world_bank")
        build_staging_world_bank(
            raw_dir=RAW_DIR / "world_bank",
            output_path=STAGING_DIR / "world_bank.parquet",
        )
        results["world_bank"] = True
    except Exception:
        logger.exception("Failed to build world_bank staging")
        results["world_bank"] = False

    logger.info("Staging results: %s", results)

    if all(results.values()):
        logger.info("All staging outputs built successfully.")
        return 0

    failed = [k for k, v in results.items() if not v]
    logger.error("Failed staging builds: %s", failed)
    return 1


if __name__ == "__main__":
    sys.exit(main())