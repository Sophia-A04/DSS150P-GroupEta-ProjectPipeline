import logging
import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(log_dir: Path = Path("logs")):
    """Configure file + console logging for ingestion."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"ingestion_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    logger.info("Logging initialized. Log file: %s", log_file)

def get_batch_id() -> str:
    """Return a UTC timestamp-based batch identifier."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def record_metadata(
    source_name: str,
    output_path: Path,
    batch_id: str,
    extra: dict = None,
):
    """Write a JSON metadata sidecar next to the raw file."""
    meta = {
        "source": source_name,
        "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "batch_id": batch_id,
        "output_file": str(output_path),
        "file_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
    }
    if extra:
        meta.update(extra)

    meta_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Metadata written to %s", meta_path)

def download_file(
    url: str,
    dest_path: Path,
    source_name: str,
    batch_id: str,
    timeout: int = 120,
    chunk_size: int = 8192,
    extra_meta: dict = None,
) -> bool:
    """
    Download a file from a URL with streaming, error handling, and metadata.
    Returns True on success, False on failure.
    """
    logger.info("[%s] Starting download from %s", source_name, url)
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            total_bytes = 0
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)

        logger.info("[%s] Downloaded %s bytes to %s", source_name, total_bytes, dest_path)
        record_metadata(source_name, dest_path, batch_id, extra_meta)
        return True

    except requests.exceptions.HTTPError as e:
        logger.error("[%s] HTTP error: %s", source_name, e)
    except requests.exceptions.ConnectionError as e:
        logger.error("[%s] Connection error: %s", source_name, e)
    except requests.exceptions.Timeout as e:
        logger.error("[%s] Request timed out: %s", source_name, e)
    except requests.exceptions.RequestException as e:
        logger.error("[%s] Request failed: %s", source_name, e)
    except OSError as e:
        logger.error("[%s] File system error: %s", source_name, e)

    return False