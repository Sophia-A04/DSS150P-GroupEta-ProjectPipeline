from __future__ import annotations

import shutil
import time
from pathlib import Path

import pandas as pd
import pyarrow.dataset as ds


def write_partitioned(df: pd.DataFrame, out_dir: Path, key: str = "country") -> dict:
    if key not in df.columns:
        raise ValueError(f"Partition key '{key}' is not a column.")
    if df[key].isna().any():
        raise ValueError(f"Partition key '{key}' contains nulls; fix before partitioning.")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    df.to_parquet(out_dir, partition_cols=[key], index=False)
    sizes = df.groupby(key).size()
    return {"key": key, "partitions": int(sizes.size), "rows": int(len(df)),
            "largest": (str(sizes.idxmax()), int(sizes.max())),
            "smallest": (str(sizes.idxmin()), int(sizes.min()))}


def read_partitions(out_dir: Path, key: str, values, columns=None) -> pd.DataFrame:
    values = [str(v) for v in values]
    df = pd.read_parquet(out_dir, filters=[(key, "in", values)], columns=columns)
    if key in df.columns:
        df[key] = df[key].astype(str)
    return df


def count_fragments(out_dir: Path, key: str, values) -> tuple:
    dataset = ds.dataset(out_dir, format="parquet", partitioning="hive")
    total = len(list(dataset.get_fragments()))
    selected = len(list(dataset.get_fragments(filter=ds.field(key).isin([str(v) for v in values]))))
    return selected, total


def timed_comparison(full_df_loader, out_dir: Path, key: str, values, repeats: int = 3) -> dict:
    def best(fn):
        times = []
        for _ in range(repeats):
            start = time.perf_counter()
            result = fn()
            times.append(time.perf_counter() - start)
        return min(times), result

    values = [str(v) for v in values]
    full_s, full = best(lambda: full_df_loader()[lambda d: d[key].astype(str).isin(values)])
    part_s, part = best(lambda: read_partitions(out_dir, key, values))
    selected, total = count_fragments(out_dir, key, values)
    return {"full_scan_s": round(full_s, 4), "partition_read_s": round(part_s, 4),
            "rows_full_scan": int(len(full)), "rows_partition_read": int(len(part)),
            "fragments_read": selected, "fragments_total": total}