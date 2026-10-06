# Known Issues, Limitations, and Assumptions

## Data-Quality Warnings

These are accepted as facts of the source data, not fixed by the pipeline, and surfaced so downstream consumers can filter explicitly.

### 1. WRI negative generation values

`generation_gwh_2019`, and earlier `generation_gwh_YYYY` columns, can contain negative values. This is a source-side issue in the WRI Global Power Plant Database. The raw WRI validator classifies it as a warning, not an error, and the value is retained to preserve source fidelity. Downstream analytics that require non-negative generation should filter `generation_gwh_2019 >= 0` explicitly.

### 2. World Bank blank ISO codes

5 of 265 raw World Bank entities have a blank `countryiso3code`, which corresponds to World Bank regional and aggregate entities such as regions or income groups. These are excluded from the staging table, which has 260 rows. The raw validator reports this as a warning. The exclusion rule is that `countryiso3code` must match three uppercase letters before the entity participates in a country join.

### 3. Unmatched plants

Some plants belong to countries that have no OWID 2019 record or no World Bank 2019 record. These rows are retained with null country-level values and explicit flags. `owid_2019_matched` is False for the 9 plants without an OWID row. `wb_2019_matched` is False for the 50 plants without a World Bank row.

Rationale: dropping these plants would break the one-row-per-plant grain that the project problem statement depends on. The trade-off is deliberate: coverage gaps are surfaced as flags, not silently closed.

### 4. World Bank matched but GDP null

The integrated validator check `wb_matched_rows_have_values` reports 40 rows where `wb_2019_matched` is True but `wb_gdp_current_usd` is null. Root cause: the World Bank 2019 slice for some matched countries does not include GDP in the current API response. This is a warning, not an error. Consumers that require GDP should filter `wb_gdp_current_usd IS NOT NULL`.

### 5. Owner field encoding artifacts

Some `owner` values carry CSV encoding artifacts from the WRI source, for example `SociÃ©te AlgÃ©rienne de Production de l'ElectricitÃ©` instead of the correct French name. The values are retained as-is to preserve source fidelity and are not normalised in the curated layer.

## Pipeline Limitations

### DAG wiring for curated transform and Postgres load

On `origin/main`, the Airflow DAG previously had `transform_curated` and `load_postgres` as placeholders. The real implementations (`src/transform/run_curated.py` and `src/load/`) exist on `main`. Whether the DAG is currently wired to them depends on the latest DAG state. Gab owns the DAG.

### validate_curated flag on the DAG

The validator supports `--skip-if-missing`, which returns exit code 99 so Airflow can skip the task through `skip_on_exit_code=99` when no curated dataset exists. Whether the DAG task uses this flag depends on the current DAG state. Gab owns the DAG. The validator behavior itself is tested and verified in `tests/test_integration_skip_if_missing.py`.

### Postgres tests

Postgres loader tests exercise insert logic but do not spin up a live database in CI. This is acceptable for the class project scope but is a limitation for full end-to-end verification.

## Assumptions

- ISO-3 country codes are the join key between plant and country-level sources.
- 2019 is the reference year for country indicators.
- Plant-level grain is non-negotiable; country joins are many-to-one.
- OWID and World Bank coverage gaps are facts to be flagged, not errors to be fixed by dropping plants.

## Not Attempted

- No synthetic data was added at any layer.
- No destructive preprocessing of raw sources.
- No imputation of missing values in country indicators.
- No correction of source-side encoding artifacts in the `owner` field.

## Traceability

Every warning in this document corresponds to a named check in a rule module and can be reproduced by re-running the relevant CLI on the committed datasets. Warnings appear in validation log output with their failing row counts and are not silent.
