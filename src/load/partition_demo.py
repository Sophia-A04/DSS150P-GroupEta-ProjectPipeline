from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.validate.integration_validation import find_curated
from src.validate.reporting import PROJECT_ROOT, configure_logging, logger

from .format_benchmark import read_any
from .partitioning import timed_comparison, write_partitioned

DOCS_DIR = PROJECT_ROOT / "docs" / "file_formats"
PARTITION_DIR = PROJECT_ROOT / "data" / "curated" / "partitioned_demo"

RATIONALE = [
    "`country` (ISO-3) is the join key to OWID and World Bank and the unit of analysis: national power-generation "
    "profiles, fuel-mix clustering and Philippine-specific findings all filter or aggregate by country.",
    "Cardinality is moderate (about 160 to 170 values), so a country query reads one small partition while the "
    "number of files stays manageable.",
    "Partitions are uneven (a few countries hold thousands of plants, many hold only a handful); this is accepted "
    "because queries are country-first and every partition remains small in absolute size.",
    "Alternatives considered: `primary_fuel` (15 balanced values, but analysis is not fuel-first), "
    "`commissioning_year` (many missing values, so nulls would need a separate partition), and no partitioning "
    "(every Philippine query would scan all plants).",
    "Rerun safety: the target directory is replaced on every write, so repeated runs never duplicate files or rows.",
]


def write_report(summary, stats, input_path, key, values, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out_dir / "partitioning_report.json").write_text(json.dumps(
        {"generated_at_utc": stamp, "input": str(input_path), "summary": summary,
         "comparison": stats, "selected_values": values}, indent=2), encoding="utf-8")
    speedup = stats["full_scan_s"] / stats["partition_read_s"] if stats["partition_read_s"] else 0
    lines = [
        "# Partitioning Report", "",
        f"- Generated (UTC): {stamp}",
        f"- Input: `{input_path.name}`",
        f"- Partition key: `{key}` (Hive-style directories, Parquet files)",
        f"- Partitions: {summary['partitions']} for {summary['rows']:,} rows",
        f"- Largest partition: {summary['largest'][0]} ({summary['largest'][1]:,} rows)",
        f"- Smallest partition: {summary['smallest'][0]} ({summary['smallest'][1]:,} rows)", "",
        f"## Selective read: {', '.join(values)}", "",
        "| method | seconds | rows returned | files read |", "|---|---|---|---|",
        f"| full scan then filter | {stats['full_scan_s']} | {stats['rows_full_scan']} | all |",
        f"| partition read | {stats['partition_read_s']} | {stats['rows_partition_read']} | "
        f"{stats['fragments_read']} of {stats['fragments_total']} |", "",
        f"Partition pruning reads {stats['fragments_read']} of {stats['fragments_total']} files "
        f"({speedup:.1f}x faster than the full scan in this run).", "",
        "## Rationale for the partition key", ""] + [f"- {r}" for r in RATIONALE] + [""]
    (out_dir / "partitioning_report.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Write a partitioned Parquet dataset and read selected partitions.")
    parser.add_argument("--input", default=None, help="csv or parquet file (default: curated dataset)")
    parser.add_argument("--key", default="country")
    parser.add_argument("--values", nargs="+", default=["PHL"])
    args = parser.parse_args(argv)

    configure_logging()
    path = Path(args.input) if args.input else find_curated()
    if path is None or not path.exists():
        logger.error("No input dataset found; pass --input.")
        return 1
    df = read_any(path)
    try:
        summary = write_partitioned(df, PARTITION_DIR, args.key)
    except ValueError as exc:
        logger.error("Partitioning failed: %s", exc)
        return 1
    logger.info("Wrote %d partitions (%d rows) to %s", summary["partitions"], summary["rows"], PARTITION_DIR)
    stats = timed_comparison(lambda: read_any(path), PARTITION_DIR, args.key, args.values)
    if stats["rows_full_scan"] != stats["rows_partition_read"]:
        logger.error("Partition read returned %d rows but full scan returned %d",
                     stats["rows_partition_read"], stats["rows_full_scan"])
        return 1
    logger.info("Selective read %s: %d rows from %d of %d files; full scan %ss vs partition %ss",
                args.values, stats["rows_partition_read"], stats["fragments_read"],
                stats["fragments_total"], stats["full_scan_s"], stats["partition_read_s"])
    write_report(summary, stats, path, args.key, args.values, DOCS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())