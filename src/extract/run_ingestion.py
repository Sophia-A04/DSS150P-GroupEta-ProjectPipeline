print(">>> run_ingestion.py is executing <<<")
"""
Entry point for automated ingestion of all approved data sources.
Usage:
    python -m src.extract.run_ingestion
"""
import logging
import sys
from .config import DATA_RAW_DIR, LOGS_DIR
from .ingestion_utils import setup_logging, get_batch_id
from .ingest_wri import ingest_wri
from .ingest_owid import ingest_owid
from .ingest_world_bank import ingest_world_bank

logger = logging.getLogger(__name__)

def main() -> int:
    setup_logging(LOGS_DIR)
    batch_id = get_batch_id()
    logger.info("Starting ingestion batch: %s", batch_id)

    results = {
        "wri": ingest_wri(DATA_RAW_DIR, batch_id),
        "owid": ingest_owid(DATA_RAW_DIR, batch_id),
        "world_bank": ingest_world_bank(DATA_RAW_DIR, batch_id),
    }

    logger.info("Ingestion results: %s", results)

    if all(results.values()):
        logger.info("All ingestions succeeded.")
        return 0
    else:
        failed = [k for k, v in results.items() if not v]
        logger.error("Failed ingestions: %s", failed)
        return 1

if __name__ == "__main__":
    sys.exit(main())