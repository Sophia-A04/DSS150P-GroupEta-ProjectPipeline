import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from .ingestion_utils import record_metadata

logger = logging.getLogger(__name__)

WORLD_BANK_BASE = "https://api.worldbank.org/v2"
WB_YEAR = "2019"

INDICATORS = {
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "population": "SP.POP.TOTL",
    "gdp_current_usd": "NY.GDP.MKTP.CD",
}

def ingest_world_bank(raw_dir: Path, batch_id: str) -> bool:
    """Fetch World Bank indicators and save raw JSON responses."""
    out_dir = raw_dir / "world_bank"
    out_dir.mkdir(parents=True, exist_ok=True)
    overall_success = True

    for name, indicator_code in INDICATORS.items():
        url = (
            f"{WORLD_BANK_BASE}/country/all/indicator/{indicator_code}"
            f"?format=json&per_page=20000&date={WB_YEAR}"
        )
        dest = out_dir / f"world_bank_{name}.json"
        logger.info("[world_bank] Fetching %s from %s", name, url)

        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) < 2:
                logger.error("[world_bank] Invalid response structure for %s", name)
                overall_success = False
                continue

            dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.info("[world_bank] Saved %s to %s", name, dest)

            record_metadata(
                source_name=f"world_bank_{name}",
                output_path=dest,
                batch_id=batch_id,
                extra={"indicator_code": indicator_code, "format": "json",
                       "year": WB_YEAR},
            )

        except requests.exceptions.RequestException as e:
            logger.error("[world_bank] Request failed for %s: %s", name, e)
            overall_success = False
        except (ValueError, json.JSONDecodeError) as e:
            logger.error("[world_bank] Invalid JSON for %s: %s", name, e)
            overall_success = False

    if overall_success:
        logger.info("World Bank ingestion completed successfully.")
    else:
        logger.error("World Bank ingestion encountered errors.")
    return overall_success