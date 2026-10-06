# Validation Documentation

## Philosophy

Validation runs per layer: raw, staging, integrated and curated. Each layer has a dedicated rule module and a CLI that returns explicit exit codes. Failures surface through logs, exceptions, pytest, and report artifacts, so a broken pipeline is visible rather than silent.

## Framework

| File | Role |
|---|---|
| `src/validate/checks.py` | Reusable check primitives |
| `src/validate/reporting.py` | Logging and report emission |
| `src/validate/profiling.py` | Column profiling helpers |
| `src/validate/wri_rules.py` | WRI-specific rules |
| `src/validate/owid_rules.py` | OWID-specific rules |
| `src/validate/world_bank_rules.py` | World Bank-specific rules |
| `src/validate/raw_validation.py` | Raw-layer CLI |
| `src/validate/staging_rules.py` | Staging-layer rules |
| `src/validate/staging_validation.py` | Staging-layer CLI |
| `src/validate/integration_rules.py` | Integrated and curated rules |
| `src/validate/integration_validation.py` | Integrated and curated CLI |

## Raw-Layer Results

| Source | Checks | Errors | Warnings | Warning detail |
|---|---|---|---|---|
| WRI | 16 | 0 | 1 | Negative `generation_gwh_2019` values |
| OWID | 16 | 0 | 0 | None |
| World Bank | 13 | 0 | 1 | Blank `countryiso3code` for regional aggregates |

## Staging-Layer Results

| Table | Checks | Errors | Warnings | Rows |
|---|---|---|---|---|
| `stg_powerplants` | 11 | 0 | 0 | 34,936 |
| `stg_owid_2019` | 12 | 0 | 0 | 218 |
| `stg_world_bank_2019` | 13 | 0 | 0 | 260, with 5 blank-ISO entities excluded from 265 |

Cross-source staging checks produced 0 errors and 2 warnings. There are 9 plants without an OWID match and 50 plants without a World Bank match. Both warnings are intentional because dropping those plants would break the one-row-per-plant grain.

## Integrated and Curated-Layer Results

Command: `python -m src.validate.integration_validation`.

Dataset: `data/curated/eta_curated_2019.parquet`.

Latest run: 24 checks, 0 errors, 1 warning.

Warning: `wb_matched_rows_have_values` reports 40 rows flagged as WB-matched that have no GDP value. This is a coverage fact, not a pipeline defect. See `docs/known_issues.md`.

Sample of the raw log output:

```text
INFO | PASS | integrated_2019 | schema            | required_columns_present          | failed=0 | OK
INFO | PASS | integrated_2019 | uniqueness        | unique_gppd_idnr                  | failed=0 | OK
INFO | PASS | integrated_2019 | row_count         | row_count_preserved               | failed=0 | OK
INFO | PASS | integrated_2019 | business_rule     | phl_rows_matched_to_sources       | failed=0 | OK
WARN | WARN | integrated_2019 | business_rule     | wb_matched_rows_have_values       | failed=40 | 40 rows flagged as World Bank matched have no GDP value
INFO | integrated_2019 validation PASSED: 24 checks, 0 errors, 1 warnings
```

## Check Types Implemented

The rubric requires at least five meaningful automated check types. This pipeline implements ten, spread across three layers.

1. Schema correctness
2. Data types
3. Nullability
4. Uniqueness
5. Duplicates
6. Accepted values
7. Numeric ranges
8. ISO-code validity
9. Referential integrity
10. Row-count and business rules, including Philippines presence, 2019 presence, and capacity totals consistency

## CLI Contract for `integration_validation.py`

| Command | Behaviour |
|---|---|
| `python -m src.validate.integration_validation` | Validate `data/curated/`. Exit 0 on pass, 1 on fail, 1 on missing when no flag is given |
| `python -m src.validate.integration_validation --skip-if-missing` | Exit 99 if `data/curated/` is empty, so Airflow can skip through `skip_on_exit_code=99` |
| `python -m src.validate.integration_validation --path <file>` | Validate an explicit dataset. A missing path exits 1 and is never skipped |

## How to Run

```powershell
python -m src.validate.raw_validation
python -m src.validate.staging_validation
python -m src.validate.integration_validation
python -m pytest -q
```

## Failure Visibility

Nonzero exit codes use 0 for pass, 1 for failure, and 99 for a requested skip. The validator calls `logger.error` with the failing check name, raises `ValidationError` with a human-readable message, and participates in pytest assertions. Report artifacts, when applicable, are written under `docs/profiling/`.

## Traceability

Every warning in this document corresponds to a named check in a rules module and can be reproduced by re-running the CLI above on the committed datasets. Warnings are not silent. They are logged with the failing row count.
