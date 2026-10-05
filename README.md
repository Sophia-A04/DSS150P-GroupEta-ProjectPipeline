# DSS150P Group Eta Project Pipeline

## Data Engineering Pipeline for Evaluating National Energy Decoupling and Fuel-Mix Transitions

### Course

DSS150P — Fundamentals of Data Engineering

### Group Eta Members

- Sophia Abad
- Mar Gabriel Toliba
- Thiareze Barrios

---

## Project Overview

This project develops a reproducible data engineering pipeline that integrates global power plant data with national carbon-emissions, economic, and demographic indicators.

The project aims to support analysis of how national power-generation profiles and installed generation capacity relate to carbon emissions, economic activity, and energy-transition patterns.

The project will eventually support country-level comparisons, clustering, and scenario-based analysis of alternative fuel-mix configurations.

---

## Data Sources

The project currently uses three approved data sources:

### 1. Global Power Plant Database (WRI)

Provides plant-level information including:

- Power plant identifiers
- Plant names
- Country information
- Installed generation capacity
- Primary fuel
- Geographic coordinates
- Other available plant characteristics

### 2. Our World in Data (OWID) CO₂ and Greenhouse Gas Emissions Dataset

Provides national emissions and carbon-related indicators.

The reference integration uses a 2019 country-level snapshot.

OWID is treated as the primary source for emissions-related indicators used in the integrated dataset.

### 3. World Bank Indicators REST API

Provides national economic and demographic indicators.

The reference prototype uses 2019 values for:

- GDP (current US$)
- Population, total
- GDP per capita (current US$)

The three sources are integrated primarily through ISO-3 country codes.

---

## Reference Integration Prototype

The validated three-source reference prototype is stored in:

`notebooks/01_merge_prototype.ipynb`

The notebook integrates:

**Global Power Plant Database + OWID 2019 indicators + World Bank 2019 indicators**

The Global Power Plant Database remains the base dataset.

The natural analytical grain of the final integrated dataset is:

**ONE ROW = ONE REAL POWER PLANT**

Country-level information from OWID and the World Bank is attached to individual plant records using ISO-3 country codes.

Country-level installed-capacity features are calculated separately and then joined back to the plant-level dataset.

---

## Integration Rules

The reference implementation follows these main integration rules:

- The Global Power Plant Database remains at plant-level grain.
- `gppd_idnr` is treated as the plant identifier.
- ISO-3 country codes are used for country-level integration.
- OWID provides emissions and carbon-related indicators.
- World Bank provides the selected economic and demographic indicators.
- GDP and population fields available from OWID are not used as the primary economic and demographic measures in the final analytical merge.
- Country-level enrichment tables should contain only one applicable record per ISO-3 code for the 2019 snapshot.
- Many-to-one relationships are expected when country-level data are joined to plant records.
- Left joins are used to preserve legitimate power plant records.
- Missing country-level indicators remain missing when no valid source match is available.
- Missing values are not automatically interpreted as zero.
- World Bank aggregate or regional entities should not create artificial plant matches.
- Country-level installed-capacity features are joined back to plant-level records without changing the final analytical grain.

Detailed integration assumptions are documented in:

`docs/integration/integration_rules.md`

---

## Validated Prototype Characteristics

The current three-source reference output contains approximately:

- 34,936 plant rows
- 34,936 unique `gppd_idnr` values
- 167 countries
- 123 Philippine plant rows
- 34,927 OWID-matched plant rows
- 34,886 World Bank-matched plant rows

These values serve as regression references for later production-pipeline development.

They are not intended to be manually hard-coded into the final transformation pipeline.

---

## Philippines Validation

The Philippines is retained in the three-source integrated dataset.

The validated prototype contains approximately 123 Philippine plant records.

Philippine plant records retain:

- WRI plant-level information
- OWID 2019 emissions indicators
- World Bank 2019 economic and demographic indicators
- Engineered installed-capacity features

The current Philippines checks are primarily integration-integrity checks.

A more detailed Philippine-context analysis will be completed during a later project phase.

---

## Important Terminology

### Installed Generation Capacity

`capacity_mw` represents installed generation capacity.

It describes the amount of generating capacity installed at a power plant.

### Actual Electricity Generation

Generation fields such as `generation_gwh` represent actual electricity generation where available.

Therefore:

- Installed-capacity shares are not equivalent to electricity-generation shares.
- Missing generation values are not interpreted as zero generation.
- Generation data are not required to preserve the plant-level analytical grain.

---

## Repository Structure

The repository is organized into major data-engineering components:

- `notebooks/` — exploratory and reference prototype notebooks
- `data/raw/` — source-faithful ingested data
- `data/staging/` — cleaned and standardized intermediate datasets
- `data/curated/` — validated analytical datasets
- `src/extract/` — automated source-ingestion components
- `src/transform/` — production transformation and integration modules
- `src/validate/` — reusable data-quality validation logic
- `src/load/` — output and loading utilities
- `dags/` — Apache Airflow DAG definitions
- `sql/` — PostgreSQL schemas and queries
- `tests/` — automated tests
- `config/` — project configuration
- `logs/` — pipeline execution logs
- `docs/` — architecture, profiling, integration, and project documentation
- `outputs/` — generated analytical outputs

---

## Data Layers

The production pipeline follows a layered architecture:

**RAW → STAGING → CURATED**

### Raw Layer

Contains source-faithful data retrieved from the approved external sources.

Raw data should remain as close as practical to the retrieved source representation.

### Staging Layer

Contains cleaned and standardized source-specific datasets prepared for integration.

Typical staging operations may include:

- Type conversion
- Column standardization
- Year filtering
- ISO-code normalization
- Source-specific cleaning
- Removal of unnecessary fields
- Preparation of one-record-per-country snapshots where required

### Curated Layer

Contains validated analytical datasets created through integration of the staging-layer sources.

The final integrated analytical dataset preserves the plant-level grain.

---

## Current Development Status

The repository currently contains working foundations or implementations for:

- Git-based collaborative development
- Automated source ingestion
- Raw data storage
- Raw-source profiling
- Automated data-quality validation
- Staging validation rules
- Integration validation rules
- CSV, JSON, and Parquet format benchmarking
- Docker environment foundation
- PostgreSQL service foundation
- Apache Airflow orchestration scaffold
- Validated three-source reference integration notebook
- Three-source integration rules and assumptions

The modular production transformation layer under `src/transform/` remains a major upcoming implementation stage.

The reference notebook will serve as the validated baseline when its transformation logic is converted into reusable Python modules.

---

## Reproducibility Goal

The final project is intended to recreate the analytical dataset from the approved source data without depending on a manually prepared final CSV.

The intended production flow is:

**Source Ingestion → Raw Validation → Staging Transformation → Staging Validation → Curated Integration → Curated Validation → PostgreSQL Loading**

The repository should contain the code, configuration, validation rules, environment definitions, and documentation required to reproduce the pipeline.

Generated datasets are excluded from normal Git tracking where appropriate.

The manually produced prototype output may be used as a regression reference, but the production pipeline should recreate the intended result directly from the approved sources.

---

## Validation Approach

The project uses automated validation across multiple pipeline stages.

Validation areas include:

- Required-column checks
- Data-type checks
- Nullability checks
- Uniqueness checks
- Duplicate-row checks
- ISO-code format checks
- Accepted-value checks
- Numerical range checks
- Row-count sanity checks
- Referential-integrity checks
- Plant-grain preservation
- Philippines-preservation checks
- Source-match consistency checks

The validation framework is maintained under:

`src/validate/`

---

## Collaboration Workflow

Development is performed through feature branches rather than directly on `main`.

General workflow:

1. Update local `main` from `origin/main`.
2. Create a task-specific feature branch.
3. Complete the assigned work.
4. Review local changes.
5. Create meaningful commits.
6. Push the feature branch.
7. Open a Pull Request targeting `main`.
8. Review and test the Pull Request.
9. Resolve conflicts or review comments where necessary.
10. Merge approved work into `main`.

The shared `main` branch represents the latest reviewed and accepted project state.

---

## Development Direction

The project will continue by:

- Converting reference notebook logic into reusable transformation modules
- Completing RAW → STAGING → CURATED processing
- Integrating transformation tasks into Airflow
- Completing PostgreSQL loading and retrieval
- Expanding automated testing
- Implementing partitioning
- Completing reproducibility and idempotency testing
- Finalizing architecture and data-flow documentation
- Conducting Philippine-context analysis
- Performing final repository and documentation QA

---

## Current Reference Files

Three-source integration prototype:

`notebooks/01_merge_prototype.ipynb`

Integration assumptions and rules:

`docs/integration/integration_rules.md`

The notebook is a validated reference implementation and should not be treated as the final production pipeline.