from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.validate.integration_validation import find_curated
from src.validate.reporting import PROJECT_ROOT, configure_logging, logger

from .file_formats import DEFAULT_SUBSET, benchmark

DOCS_DIR = PROJECT_ROOT / "docs" / "file_formats"
WORK_DIR = PROJECT_ROOT / "outputs" / "format_benchmark"

TRADE_OFFS = [
    "CSV: plain text, universally readable, no schema; types are re-inferred on every read, "
    "so dates and codes can change type; the whole file is parsed even when few columns are needed.",
    "JSON: self-describing and suitable for API payloads, but repeats every field name on every record, "
    "giving the largest files and slowest reads; no native date or integer/float distinction guarantees.",
    "Parquet: columnar and compressed, stores the schema, reads selected columns without parsing the rest, "
    "and supports partitioned datasets; requires a library (pyarrow) and is not human-readable.",
]


def read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def write_report(rows, input_path: Path, df: pd.DataFrame, repeats: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    csv_size = next(r["size_mb"] for r in rows if r["format"] == "csv")
    smallest = min(rows, key=lambda r: r["size_mb"])
    fastest_read = min(rows, key=lambda r: r["read_all_s"])
    fastest_subset = min(rows, key=lambda r: r["read_subset_s"])

    (out_dir / "format_comparison.json").write_text(json.dumps({
        "generated_at_utc": stamp, "input": str(input_path), "rows": len(df),
        "columns": int(df.shape[1]), "repeats": repeats, "results": rows}, indent=2), encoding="utf-8")

    lines = [
        "# File Format Comparison", "",
        f"- Generated (UTC): {stamp}",
        f"- Input: `{input_path.name}`",
        f"- Rows x columns: {len(df):,} x {df.shape[1]}",
        f"- Timing: median of {repeats} runs",
        f"- Subset read: columns {', '.join(c for c in DEFAULT_SUBSET if c in df.columns)}", "",
        "| format | size (MB) | vs CSV | write (s) | read all (s) | read subset (s) | dtype mismatches |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ratio = f"{r['size_mb'] / csv_size:.2f}x" if csv_size else ""
        lines.append(f"| {r['format']} | {r['size_mb']} | {ratio} | {r['write_s']} | "
                     f"{r['read_all_s']} | {r['read_subset_s']} | {r['dtype_mismatches']} |")
    lines += ["", "## Observations", "",
              f"- Smallest file: {smallest['format']} ({smallest['size_mb']} MB).",
              f"- Fastest full read: {fastest_read['format']} ({fastest_read['read_all_s']} s).",
              f"- Fastest subset read: {fastest_subset['format']} ({fastest_subset['read_subset_s']} s).", ""]
    for r in rows:
        if r["mismatched_columns"]:
            lines.append(f"- Schema change after round trip in {r['format']}: {', '.join(r['mismatched_columns'])}.")
        else:
            lines.append(f"- {r['format']}: schema preserved for all columns.")
    lines += ["", "## Trade-offs", ""] + [f"- {t}" for t in TRADE_OFFS] + [""]
    (out_dir / "format_comparison.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare CSV, JSON and Parquet.")
    parser.add_argument("--input", default=None, help="csv or parquet file (default: curated dataset)")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args(argv)

    configure_logging()
    path = Path(args.input) if args.input else find_curated()
    if path is None or not path.exists():
        logger.error("No input dataset found; pass --input.")
        return 1
    logger.info("Benchmarking formats on %s", path)
    df = read_any(path)
    rows = benchmark(df, WORK_DIR, args.repeats)
    write_report(rows, path, df, args.repeats, DOCS_DIR)
    for r in rows:
        logger.info("%s | %s MB | write %ss | read %ss | subset %ss | dtype mismatches %d",
                    r["format"], r["size_mb"], r["write_s"], r["read_all_s"],
                    r["read_subset_s"], r["dtype_mismatches"])
    logger.info("Report written to %s", DOCS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())