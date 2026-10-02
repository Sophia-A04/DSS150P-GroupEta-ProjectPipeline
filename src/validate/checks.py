from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable, Optional

import pandas as pd

ISO3_PATTERN = re.compile(r"^[A-Z]{3}$")


class ValidationError(Exception):
    pass


@dataclass
class CheckResult:
    source: str
    check_type: str
    check_name: str
    passed: bool
    severity: str
    failed_count: int
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


def _make(source, check_type, name, failed_count, detail_if_failed, severity):
    failed_count = int(failed_count)
    return CheckResult(
        source=source,
        check_type=check_type,
        check_name=name,
        passed=failed_count == 0,
        severity=severity,
        failed_count=failed_count,
        detail="OK" if failed_count == 0 else detail_if_failed,
    )


def _null_mask(series: pd.Series) -> pd.Series:
    mask = series.isna()
    if not pd.api.types.is_numeric_dtype(series):
        blank = series.astype("string").str.strip().eq("").fillna(False)
        mask = mask | blank.astype(bool)
    return mask


def check_schema(df, source, required_columns: Iterable[str], severity="error"):
    missing = [c for c in required_columns if c not in df.columns]
    return _make(source, "schema", "required_columns_present", len(missing),
                 f"missing columns: {missing}", severity)


def check_dtypes(df, source, expected: dict, severity="error"):
    bad = []
    for col, kind in expected.items():
        if col not in df.columns:
            continue
        s = df[col]
        if kind == "numeric":
            ok = pd.api.types.is_numeric_dtype(s)
        elif kind == "string":
            ok = pd.api.types.is_string_dtype(s) or s.dtype == object
        else:
            raise ValueError(f"Unknown dtype kind: {kind}")
        if not ok:
            bad.append(f"{col}: expected {kind}, found {s.dtype}")
    return _make(source, "data_type", "expected_dtypes", len(bad), "; ".join(bad), severity)


def check_not_null(df, source, columns: Iterable[str], severity="error"):
    problems = {}
    for col in columns:
        if col in df.columns:
            n = int(_null_mask(df[col]).sum())
            if n:
                problems[col] = n
    return _make(source, "nullability", "required_fields_not_null",
                 sum(problems.values()), f"null/blank counts: {problems}", severity)


def check_null_rate(df, source, column, max_rate: float, severity="warning"):
    if column not in df.columns or len(df) == 0:
        return _make(source, "completeness", f"{column}_null_rate", 0, "", severity)
    rate = float(_null_mask(df[column]).mean())
    failed = 1 if rate > max_rate else 0
    return _make(source, "completeness", f"{column}_null_rate", failed,
                 f"null rate {rate:.1%} exceeds allowed {max_rate:.1%}", severity)


def check_unique(df, source, columns, severity="error"):
    columns = [columns] if isinstance(columns, str) else list(columns)
    if any(c not in df.columns for c in columns):
        return _make(source, "uniqueness", f"unique_{'+'.join(columns)}", 0, "", severity)
    n = int(df.duplicated(subset=columns, keep="first").sum())
    return _make(source, "uniqueness", f"unique_{'+'.join(columns)}", n,
                 f"{n} duplicate key rows on {columns}", severity)


def check_duplicate_rows(df, source, severity="error"):
    n = int(df.duplicated().sum())
    return _make(source, "duplicates", "no_fully_duplicated_rows", n,
                 f"{n} fully duplicated rows", severity)


def check_accepted_values(df, source, column, allowed, allow_null=False, severity="error"):
    if column not in df.columns:
        return _make(source, "accepted_values", f"{column}_accepted_values", 0, "", severity)
    s = df[column]
    invalid = ~s.isin(list(allowed))
    if allow_null:
        invalid &= s.notna()
    bad_values = sorted(map(str, s[invalid].dropna().unique()))[:10]
    return _make(source, "accepted_values", f"{column}_accepted_values", invalid.sum(),
                 f"{int(invalid.sum())} rows outside accepted set; examples: {bad_values}", severity)


def check_range(df, source, column, min_value: Optional[float] = None,
                max_value: Optional[float] = None, inclusive_min=True, severity="error"):
    name = f"{column}_range"
    if column not in df.columns:
        return _make(source, "range", name, 0, "", severity)
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    bad = pd.Series(False, index=s.index)
    if min_value is not None:
        bad |= (s < min_value) if inclusive_min else (s <= min_value)
    if max_value is not None:
        bad |= s > max_value
    return _make(source, "range", name, bad.sum(),
                 f"{int(bad.sum())} values outside [{min_value}, {max_value}]; "
                 f"observed min={s.min()}, max={s.max()}", severity)


def check_iso3_format(df, source, column, allow_null=False, severity="error"):
    name = f"{column}_iso3_format"
    if column not in df.columns:
        return _make(source, "iso_code", name, 0, "", severity)
    s = df[column]
    valid = s.astype("string").str.match(ISO3_PATTERN.pattern).fillna(False).astype(bool)
    invalid = ~valid
    if allow_null:
        invalid &= s.notna()
    examples = sorted(map(str, s[invalid].dropna().unique()))[:10]
    return _make(source, "iso_code", name, invalid.sum(),
                 f"{int(invalid.sum())} values not matching ^[A-Z]{{3}}$; examples: {examples}", severity)


def check_row_count(df, source, min_rows: int, max_rows: Optional[int] = None, severity="error"):
    n = len(df)
    bad = n < min_rows or (max_rows is not None and n > max_rows)
    return _make(source, "row_count", "row_count_sanity", int(bad),
                 f"row count {n} outside [{min_rows}, {max_rows}]", severity)


def check_contains_values(df, source, column, required_values, severity="error"):
    name = f"{column}_contains_required"
    if column not in df.columns:
        return _make(source, "business_rule", name, 0, "", severity)
    present = set(df[column].dropna().astype(str))
    missing = [str(v) for v in required_values if str(v) not in present]
    return _make(source, "business_rule", name, len(missing),
                 f"required values missing from {column}: {missing}", severity)