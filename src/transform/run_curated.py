"""
Entrypoint for the curated transformation layer.

Reads the three staging Parquet datasets and produces the
integrated plant-level curated dataset.

Usage:
    python -m src.transform.run_curated
"""

import logging
import sys
from pathlib import Path

from src.transform.integrate_sources import (
    build_curated_dataset,
)


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STAGING_DIR = (
    PROJECT_ROOT
    / "data"
    / "staging"
)

CURATED_DIR = (
    PROJECT_ROOT
    / "data"
    / "curated"
)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s"
        ),
    )

    CURATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        CURATED_DIR
        / "eta_curated_2019.parquet"
    )

    try:
        logger.info(
            "Building curated three-source dataset"
        )

        curated = build_curated_dataset(
            plants_path=(
                STAGING_DIR
                / "powerplants.parquet"
            ),
            owid_path=(
                STAGING_DIR
                / "owid.parquet"
            ),
            world_bank_path=(
                STAGING_DIR
                / "world_bank.parquet"
            ),
            output_path=output_path,
        )

        logger.info(
            "Curated dataset created: %s rows, %s unique plants",
            len(curated),
            curated["gppd_idnr"].nunique(),
        )

        logger.info(
            "Curated output: %s",
            output_path,
        )

    except Exception:
        logger.exception(
            "Failed to build curated dataset"
        )
        return 1

    logger.info(
        "Curated transformation completed successfully."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())