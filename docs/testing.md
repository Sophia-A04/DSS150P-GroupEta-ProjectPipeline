# Testing Documentation

## Framework

`pytest`. Full suite is run with `python -m pytest -q`. Current total is 211 passed as of 2026-10-07.

## Layout

The `tests/` directory contains unit and CLI tests across all four pipeline layers plus the validation framework itself.

| Test file | Focus |
|---|---|
| `test_checks.py` | Reusable check primitives |
| `test_reporting.py` | Logging and report emission |
| `test_rules.py` | Rule module behaviour |
| `test_raw_file_discovery.py` | Raw-source discovery |
| `test_raw_sources_local.py` | Raw local sources present and shaped |
| `test_world_bank_rules.py` | World Bank-specific rules |
| `test_clean_powerplants.py` | WRI cleaning rules |
| `test_clean_owid.py` | OWID cleaning rules |
| `test_clean_world_bank.py` | World Bank cleaning rules |
| `test_staging_rules.py` | Staging-layer rules |
| `test_staging_validation_cli.py` | Staging validation CLI exit codes |
| `test_run_staging.py` | Staging entry point |
| `test_capacity_features.py` | Derived capacity features |
| `test_integrate_sources.py` | Three-source integration logic |
| `test_integration_rules.py` | Integrated and curated rules |
| `test_integration_validation_cli.py` | Integrated validation CLI exit codes |
| `test_integration_skip_if_missing.py` | `--skip-if-missing` semantics, exit 99 versus 1 |
| `test_run_curated.py` | Curated entry point |
| `test_file_formats.py` | CSV, JSON, and Parquet write, read, and dtype preservation |
| `test_partitioning.py` | Partition write and selective read |
| `test_postgres_data_loader.py` | Data-loader behaviour |
| `test_postgres_loader.py` | Postgres loader behaviour |

`tests/builders.py` and `tests/builders_integrated.py` provide synthetic DataFrame fixtures so layer tests do not depend on the real 34,936-row dataset.

## Coverage by Layer

| Layer | Test focus |
|---|---|
| Raw | Schema, types, nullability, ranges, ISO validity, row counts |
| Cleaning | Standardisation and type coercion per source |
| Staging | Row-count preservation, key uniqueness, accepted values |
| Integration | Grain preservation, coverage flags, Philippines presence |
| Format and partitioning | Round-trip fidelity, partition pruning |
| Loader | Postgres insert behaviour |
| CLI | Exit codes for pass, fail, and skip |

## The `--skip-if-missing` Test

`tests/test_integration_skip_if_missing.py` asserts four behaviours:

1. Empty `data/curated` plus `--skip-if-missing` returns exit 99
2. Empty `data/curated` without the flag returns exit 1
3. An explicit `--path` to a missing file returns exit 1, never skipped
4. Curated present runs the normal validation path, returning 0 or 1 based on results

Why it exists: the Airflow DAG transform_curated task was a placeholder when validate_curated was introduced, so a strict curated validator would have failed the DAG on an empty folder. Exit 99 lets Airflow mark the task skipped through skip_on_exit_code=99 without weakening the validator when a real dataset is expected. This is the design point most likely to come up in technical defense.

## How to Run

```powershell
python -m pytest -q
python -m pytest tests\test_integration_skip_if_missing.py -v
python -m pytest tests\test_file_formats.py -v
python -m pytest tests\test_partitioning.py -v
```

## Reproducibility Note

`psycopg2-binary` is declared in both `requirements.txt` and `requirements-airflow.txt`. After every `git pull`, run `pip install -r requirements.txt` before running pytest, otherwise Sophia's loader tests will fail to import.

## Mapping to the Rubric

| Rubric item | Where it is proven |
|---|---|
| 4.8 Data quality validation, five or more checks | `test_rules.py`, `test_staging_rules.py`, `test_integration_rules.py` |
| 4.10 CSV, JSON, Parquet handling | `test_file_formats.py` |
| 4.11 Partitioning | `test_partitioning.py` |
| 4.16 Idempotency and rerun safety | `test_run_staging.py`, `test_run_curated.py` |
| 4.17 Modular Python | One test file per module, per layer |
| 4.6 Raw, Staging, Curated layers | `test_raw_sources_local.py`, staging tests, integration tests |

## Known Test Gaps

- Postgres loader tests exercise insert logic; they do not spin up a live database in CI.
- Failure-path tests exist for CLI exit codes but not for every individual rule.
- The full suite depends on the local raw files being present for the raw-source tests.
