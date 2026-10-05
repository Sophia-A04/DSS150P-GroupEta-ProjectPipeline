from __future__ import annotations

import statistics
import time
from pathlib import Path

import pandas as pd

FORMATS = {
    "csv": {
        "ext": ".csv",
        "write": lambda df, p: df.to_csv(p, index=False),
        "read": lambda p: pd.read_csv(p, low_memory=False),
        "read_cols": lambda p, cols: pd.read_csv(p, usecols=cols, low_memory=False),
    },
    "json": {
        "ext": ".json",
        "write": lambda df, p: df.to_json(p, orient="records", date_format="iso"),
        "read": lambda p: pd.read_json(p, orient="records"),
        "read_cols": lambda p, cols: pd.read_json(p, orient="records")[cols],
    },
    "parquet": {
        "ext": ".parquet",
        "write": lambda df, p: df.to_parquet(p, index=False),
        "read": lambda p: pd.read_parquet(p),
        "read_cols": lambda p, cols: pd.read_parquet(p, columns=cols),
    },
}

DEFAULT_SUBSET = ["country", "primary_fuel", "capacity_mw"]


def _median_seconds(fn, repeats: int) -> float:
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def benchmark(df: pd.DataFrame, work_dir: Path, repeats: int = 3, subset_cols=None) -> list:
    work_dir.mkdir(parents=True, exist_ok=True)
    subset = subset_cols or [c for c in DEFAULT_SUBSET if c in df.columns] or list(df.columns[:3])
    rows = []
    for name, spec in FORMATS.items():
        path = work_dir / f"benchmark{spec['ext']}"
        write_s = _median_seconds(lambda: spec["write"](df, path), repeats)
        size = path.stat().st_size
        read_s = _median_seconds(lambda: spec["read"](path), repeats)
        subset_s = _median_seconds(lambda: spec["read_cols"](path, subset), repeats)
        back = spec["read"](path)
        mismatched = [c for c in df.columns
                      if c not in back.columns or str(df[c].dtype) != str(back[c].dtype)]
        rows.append({
            "format": name,
            "size_mb": round(size / 1024 ** 2, 3),
            "write_s": round(write_s, 4),
            "read_all_s": round(read_s, 4),
            "read_subset_s": round(subset_s, 4),
            "rows_roundtrip": int(len(back)),
            "dtype_mismatches": len(mismatched),
            "mismatched_columns": mismatched,
        })
    return rows