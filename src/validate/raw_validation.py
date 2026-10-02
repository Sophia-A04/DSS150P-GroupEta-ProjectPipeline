from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from .checks import ValidationError
from .profiling import profile_dataframe, write_profile
from .reporting import PROFILE_DIR, PROJECT_ROOT, configure_logging, finalize_report, logger

SOURCES = {
    "wri": "src.validate.wri_rules",
    "owid": "src.validate.owid_rules",
    "world-bank": "src.validate.world_bank_rules",
}


def run_source(key: str, path_override: str | None = None) -> dict:
    module = importlib.import_module(SOURCES[key])
    if path_override:
        paths = [Path(path_override)]
    else:
        paths = module.locate()
        if not paths:
            raise FileNotFoundError(f"No raw file found for '{key}' under data/raw. "
                                    f"Run ingestion first or pass --path.")
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Raw file not found: {missing}")

    logger.info("Loading %s from %s", key, [str(p) for p in paths])
    df = module.load(paths)
    rel = lambda p: str(p.resolve().relative_to(PROJECT_ROOT)) if PROJECT_ROOT in p.resolve().parents else str(p)
    profile = profile_dataframe(df, module.SOURCE_NAME, ", ".join(rel(p) for p in paths))
    write_profile(profile, PROFILE_DIR)
    return finalize_report(module.validate(df), module.SOURCE_NAME, raise_on_error=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Profile and validate raw sources.")
    parser.add_argument("--source", choices=[*SOURCES, "all"], default="all")
    parser.add_argument("--path", default=None, help="Override raw file path (single source only)")
    args = parser.parse_args(argv)

    configure_logging()
    keys = list(SOURCES) if args.source == "all" else [args.source]
    failed = []
    for key in keys:
        try:
            run_source(key, args.path if len(keys) == 1 else None)
        except (FileNotFoundError, ValueError, ValidationError, ModuleNotFoundError) as exc:
            logger.error("Source '%s' did not pass: %s", key, exc)
            failed.append(key)
    if failed:
        logger.error("Raw validation FAILED for: %s", failed)
        return 1
    logger.info("Raw validation PASSED for: %s", keys)
    return 0


if __name__ == "__main__":
    sys.exit(main())