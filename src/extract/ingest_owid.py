import logging
from pathlib import Path
from .ingestion_utils import download_file

logger = logging.getLogger(__name__)

OWID_CSV_URL = "https://owid-public.owid.io/data/co2/owid-co2-data.csv"

def ingest_owid(raw_dir: Path, batch_id: str) -> bool:
    """Download the OWID CO₂ and Greenhouse Gas Emissions CSV."""
    dest = raw_dir / "owid" / "owid-co2-data.csv"
    logger.info("Starting OWID ingestion...")
    success = download_file(
        url=OWID_CSV_URL,
        dest_path=dest,
        source_name="owid_co2",
        batch_id=batch_id,
        extra_meta={"format": "csv", "description": "OWID CO2 and GHG Emissions"},
    )
    if success:
        logger.info("OWID ingestion completed successfully.")
    else:
        logger.error("OWID ingestion failed.")
    return success