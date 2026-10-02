from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

logger = logging.getLogger("validation")


def _num(x):
    return None if pd.isna(x) else round(float(x), 4)


def profile_dataframe(df: pd.DataFrame, source: str, source_file: str) -> dict:
    n = len(df)
    columns = []
    for col in df.columns:
        s = df[col]
        info = {
            "column": col,
            "dtype": str(s.dtype),
            "null_count": int(s.isna().sum()),
            "null_pct": round(float(s.isna().mean() * 100), 2) if n else 0.0,
            "unique_count": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            info.update(min=_num(s.min()), max=_num(s.max()), mean=_num(s.mean()),
                        median=_num(s.median()), std=_num(s.std()))
        else:
            top = s.dropna().astype(str).value_counts().head(3)
            info["top_values"] = {k: int(v) for k, v in top.items()}
        columns.append(info)
    return {
        "source": source,
        "source_file": source_file,
        "profiled_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "row_count": n,
        "column_count": int(df.shape[1]),
        "full_row_duplicates": int(df.duplicated().sum()),
        "memory_mb": round(float(df.memory_usage(deep=True).sum() / 1024**2), 2),
        "columns": columns,
    }


def _fmt(v):
    return "" if v is None else str(v)


def write_profile(profile: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    src = profile["source"]
    (out_dir / f"{src}_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

    lines = [
        f"# Raw Profile: {src}", "",
        f"- Source file: `{profile['source_file']}`",
        f"- Profiled at (UTC): {profile['profiled_at_utc']}",
        f"- Rows: {profile['row_count']:,}",
        f"- Columns: {profile['column_count']}",
        f"- Fully duplicated rows: {profile['full_row_duplicates']}",
        f"- Memory (MB): {profile['memory_mb']}", "",
        "| column | dtype | nulls | null % | unique | min | max |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in profile["columns"]:
        lines.append(f"| {c['column']} | {c['dtype']} | {c['null_count']} | {c['null_pct']} | "
                     f"{c['unique_count']} | {_fmt(c.get('min'))} | {_fmt(c.get('max'))} |")
    (out_dir / f"{src}_profile.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Profile written for %s -> %s", src, out_dir)