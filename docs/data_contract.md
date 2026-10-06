# Data Contract — Curated Integrated Dataset

**Contract ID:** eta-curated-2019
**Effective:** 2026-10-07
**Owner (contract):** Iya — QA / validation
**Owner (producer):** Sophia — integration
**Consumer:** PostgreSQL loader (`src/load/`), analytics, presentation

## 1. Scope

This contract governs the curated three-source, plant-level dataset produced by the Group Eta pipeline after the RAW to STAGING to CURATED flow.

Producer: `python -m src.transform.run_curated` (`src/transform/run_curated.py`).

Path: `data/curated/eta_curated_2019.parquet`.

Validator: `python -m src.validate.integration_validation`, with rules in `src/validate/integration_rules.py`.

## 2. Schema Guarantees

### 2.1 Required columns

| Column | Type | Constraint |
|---|---|---|
| `gppd_idnr` | string | unique, primary key |
| `country` | string | exactly 3 characters, ISO-3 |
| `name` | string | non-empty |
| `capacity_mw` | float64 | greater than 0 |
| `primary_fuel` | string | non-empty |
| `owid_2019_matched` | bool | one of True or False |
| `wb_2019_matched` | bool | one of True or False |

### 2.2 Optional columns

All OWID value columns, all World Bank value columns, and all WRI historical generation columns may contain nulls. Nulls in these columns are expected coverage gaps, not pipeline failures.

### 2.3 Grain

One row per power plant. Row count must equal the staging `powerplants` row count, which is 34,936. `gppd_idnr` must be unique. The set of `gppd_idnr` values must be identical before and after the merge.

## 3. Volume

| Metric | Contract value |
|---|---|
| Row count | 34,936 |
| Distinct `gppd_idnr` | 34,936 |
| Distinct `country` | 167 |
| Columns | 162 |

## 4. Quality Guarantees

The validator runs 24 checks across ten categories. Every check returns a nonzero exit code on failure. See section 6 for exit codes.

| # | Category | Check name | Meaning |
|---|---|---|---|
| 1 | schema | `required_columns_present` | All required integration columns present |
| 2 | data_type | `expected_dtypes` | Numeric, bool, and string columns have expected dtype |
| 3 | nullability | `required_fields_not_null` | Required fields never null |
| 4 | uniqueness | `unique_gppd_idnr` | `gppd_idnr` unique |
| 5 | duplicates | `no_fully_duplicated_rows` | No duplicate rows |
| 6 | iso_code | `country_iso3_format` | `country` matches three uppercase letters |
| 7 | accepted_values | `owid_2019_matched_accepted_values` | Bool only |
| 8 | accepted_values | `wb_2019_matched_accepted_values` | Bool only |
| 9 | range | `capacity_mw_range` | `capacity_mw` greater than 0 |
| 10 | range | `co2_range` | OWID CO₂ in plausible range |
| 11 | range | `wb_population_range` | Greater than or equal to 0 |
| 12 | range | `wb_gdp_current_usd_range` | Greater than or equal to 0 |
| 13 | business_rule | `country_contains_required` | Philippines present |
| 14 | business_rule | `phl_rows_matched_to_sources` | All PHL rows matched to OWID and WB |
| 15 | business_rule | `phl_wb_values_populated` | PHL WB values populated |
| 16 | business_rule | `fossil_renewable_share_not_over_100` | Sum of fuel shares not over 100 |
| 17 | business_rule | `plant_capacity_within_country_totals` | Plant capacity at most its country total |
| 18 | business_rule | `wb_matched_rows_have_values` | WB-matched rows have GDP; currently a warning, 40 rows |
| 19 | range | `country_primary_fuel_capacity_share_pct_range` | 0 to 100 |
| 20 | range | `fossil_share_pct_range` | 0 to 100 |
| 21 | range | `renewable_share_pct_range` | 0 to 100 |
| 22 | row_count | `row_count_preserved` | 34,936 rows |
| 23 | referential_integrity | `owid_match_flag_consistent` | Flag consistent with `iso_code` presence |
| 24 | referential_integrity | `wb_match_flag_consistent` | Flag consistent with `wb_iso_code` presence |

Latest run: 0 errors, 1 warning.

## 5. Coverage Rules

A plant belongs to a country with no OWID 2019 record, so `owid_2019_matched` is False and OWID value columns are null for that row. This is a warning-level coverage fact, not an error.

A plant belongs to a country with no World Bank 2019 record, so `wb_2019_matched` is False and WB value columns are null for that row. Same treatment.

Plants are never dropped to close a coverage gap. One-row-per-plant grain is the controlling invariant.

## 6. Failure Semantics

`python -m src.validate.integration_validation` returns the following exit codes.

| Condition | Exit code |
|---|---|
| Validation clean | 0 |
| Curated file missing with `--skip-if-missing` | 99 |
| Curated file missing without the flag | 1 |
| Explicit `--path` file missing | 1 |
| Validation errors | 1 |

Airflow integration expects `skip_on_exit_code=99` on the `validate_curated` task.

## 7. Change Control

Any change to the curated schema must ship in one PR that updates, together, the producing code `src/transform/integrate_sources.py`, the downstream DDL `sql/schema.sql`, the enforcing rules `src/validate/integration_rules.py`, the enforcing tests under `tests/`, this contract, and `docs/data_dictionary.md`. A change that updates the code but not this contract is a contract violation.

## 8. Non-goals

This contract does not guarantee OWID or WB coverage. It guarantees traceable nulls where coverage is missing, plus flags `owid_2019_matched` and `wb_2019_matched`, so downstream consumers can filter explicitly.

This contract does not cover the staging or raw datasets. Those are governed separately by `staging_validation.py` and `raw_validation.py`.