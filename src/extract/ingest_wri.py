import logging
from pathlib import Path
from .ingestion_utils import download_file

logger = logging.getLogger(__name__)

WRI_CSV_URL = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"

def ingest_wri(raw_dir: Path, batch_id: str) -> bool:
    """Download the WRI Global Power Plant Database CSV."""
    dest = raw_dir / "wri" / "global_power_plant_database.csv"
    logger.info("Starting WRI ingestion...")
    success = download_file(
        url=WRI_CSV_URL,
        dest_path=dest,
        source_name="wri_gppd",
        batch_id=batch_id,
        extra_meta={"format": "csv", "description": "Global Power Plant Database"},
    )
    if success:
        logger.info("WRI ingestion completed successfully.")
    else:
        logger.error("WRI ingestion failed.")
    return success