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

This project develops a reproducible data engineering pipeline that integrates global power-plant data with national carbon-emissions, economic, and demographic indicators.

The project supports analysis of how national power-generation infrastructure and installed generation capacity relate to carbon emissions, economic activity, and energy-transition patterns.

The integrated data foundation also supports a separate country-level analytical extension for clustering, Philippine benchmarking, exploratory modeling, and hypothetical installed-capacity transition scenarios. This analytical layer is implemented independently from the production data-engineering pipeline and uses the validated curated dataset as its input.

---

## Data Sources

The project uses three approved data sources.

### 1. Global Power Plant Database (WRI)

Provides plant-level information including:

- power-plant identifiers
- plant names
- country information
- installed generation capacity
- primary fuel
- geographic coordinates
- commissioning information
- generation-related fields where available
- other plant characteristics available in the source

### 2. Our World in Data (OWID) CO2 and Greenhouse Gas Emissions Dataset

Provides national emissions and carbon-related indicators.

The integration uses a 2019 country-level snapshot.

OWID is treated as the project's primary source for emissions-related indicators used in the integrated dataset.

### 3. World Bank Indicators REST API

Provides national economic and demographic indicators.

The project uses 2019 values for:

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

The notebook remains a regression reference and is not the production transformation mechanism.

---

## Integration Rules

The implementation follows these main integration rules:

- The Global Power Plant Database remains at plant-level grain.
- `gppd_idnr` is treated as the plant identifier.
- ISO-3 country codes are used for country-level integration.
- OWID provides emissions and carbon-related indicators.
- World Bank provides the selected economic and demographic indicators.
- GDP and population fields from OWID are not used as the primary economic and demographic measures in the final integration.
- Country-level enrichment tables contain no more than one applicable row per ISO-3 code for the 2019 snapshot.
- Many-to-one relationships are expected when country-level data are joined to plant records.
- Left joins preserve legitimate power-plant records.
- Missing country-level indicators remain missing when no valid source match exists.
- Missing values are not automatically interpreted as zero.
- World Bank aggregate or regional entities must not create artificial plant matches.
- Country-level installed-capacity features are joined back to plant-level records without changing the final analytical grain.

Detailed integration assumptions are documented in:

`docs/integration/integration_rules.md`

---

## Validated Integrated Dataset Characteristics

The validated three-source production output reproduces the reference plant-level characteristics:

- 34,936 plant rows
- 34,936 unique `gppd_idnr` values
- 167 countries
- 123 Philippine plant rows
- 34,927 OWID-matched plant rows
- 34,886 World Bank-matched plant rows

These values are used as regression references.

They are not manually hard-coded into the transformation pipeline.

---

## Philippines Validation and Context Analysis

The Philippines is retained throughout the three-source integrated dataset.

The validated dataset contains:

- 123 Philippine plant records
- 20,719.30 MW total installed capacity

Philippine plant records retain:

- WRI plant-level information
- OWID 2019 emissions indicators
- World Bank 2019 economic and demographic indicators
- engineered installed-capacity features

The final Philippine-context analysis includes:

- plant count
- total installed capacity
- average plant capacity
- installed capacity by primary fuel
- fossil and renewable installed-capacity shares
- national emissions indicators
- World Bank economic and demographic indicators
- largest Philippine power plants represented in the dataset
- Philippine share of installed capacity represented by the project database

The reproducible analysis is available in:

`sql/philippines_context.sql`

Interpretation is documented in:

`docs/analysis/philippines_context.md`

---

## Country-Level Clustering and Philippine Benchmarking

The completed data-engineering pipeline also supports a separate country-level analytical extension available in:

`notebooks/02_country_clustering_philippines_analysis.ipynb`

The notebook transforms the validated plant-level curated dataset into a country-level analytical dataset with the grain:

**ONE ROW = ONE COUNTRY**

The analysis addresses the question:

**Which countries have cleaner energy profiles and lower carbon emissions, and how does the Philippines compare with countries with similar energy and economic conditions?**

### Analytical Approach

The notebook includes:

- country-level aggregation of installed-capacity, emissions, and economic indicators
- K-Means clustering of countries using selected energy, carbon-intensity, and economic characteristics
- elbow and silhouette analysis for cluster selection
- cluster profiling and interpretation
- identification of the Philippine cluster
- comparison of the Philippines with potential cleaner installed-capacity benchmarks
- exploratory regression modeling of emissions-related associations
- hypothetical Philippine coal-to-renewable installed-capacity scenarios
- presentation-ready analytical visualizations

### Clustering Results

The country-level dataset contains 167 countries.

Of these, 152 countries had complete values for the selected clustering variables and were included in the final K-Means analysis. Fifteen countries were excluded because of missing clustering inputs.

The final model uses:

**K = 4 clusters**

K = 4 produced the highest silhouette score among the tested solutions at approximately 0.323 and was also supported by the elbow pattern.

The Philippines belongs to:

**Cluster 4 — Coal-heavy / higher-carbon-intensity**

This cluster contains 30 countries and has average installed-capacity shares of approximately:

- 24.9% renewable
- 69.1% fossil
- 54.9% coal

### Philippine Profile

Within the analytical dataset, the Philippines has approximately:

- 31.5% renewable installed capacity
- 68.5% fossil installed capacity
- 42.1% coal installed capacity
- 1.29 tonnes of CO2 per capita
- 0.145 CO2-per-GDP indicator

The Philippine profile is not identical to the Cluster 4 average. The Philippines has a higher renewable share and lower coal share than the average country in its cluster.

### Cleaner Installed-Capacity Benchmarks

Using same-cluster membership, economic comparability, higher renewable share, lower fossil share, and lower coal share as transparent comparison criteria, the analysis identifies:

- Morocco
- Laos
- Vietnam

as potential cleaner installed-capacity benchmarks for the Philippines.

These countries should be interpreted as comparative energy-transition references rather than models that the Philippines should directly copy.

Importantly, none of these selected benchmarks has both lower CO2 per capita and lower CO2 per GDP than the Philippines. The comparison therefore highlights differences in **installed-capacity structure**, not proof that a cleaner installed-capacity mix automatically produces lower national emissions.

### Philippine Capacity-Shift Scenarios

The notebook also evaluates hypothetical changes to the Philippine installed-capacity mix by reallocating:

- 5 percentage points
- 10 percentage points
- 20 percentage points

from coal installed capacity toward renewable installed capacity while keeping total installed capacity constant.

These scenarios illustrate changes in capacity composition only.

They are not forecasts of actual electricity generation or causal estimates of future emissions reductions.

### Analytical Limitations

The analysis uses a cross-sectional 2019 snapshot and is exploratory rather than causal.

Additional limitations include:

- installed capacity is not equivalent to actual electricity generation
- national CO2 indicators include economic activity beyond the electricity sector
- countries differ in geography, resources, electricity demand, industrial structure, grid conditions, and policy
- some countries were excluded from clustering because of missing analytical variables
- K-Means produces exploratory distance-based groupings rather than definitive country classifications
- predictive models show associations and should not be interpreted as causal emissions models

---

## Important Terminology

### Installed Generation Capacity

`capacity_mw` represents installed generation capacity.

It describes the amount of generating capacity installed at a power plant.

### Actual Electricity Generation

Generation fields such as `generation_gwh` represent actual electricity generation where available.

Therefore:

- installed-capacity shares are not equivalent to electricity-generation shares
- missing generation values are not interpreted as zero generation
- generation data are not required to preserve the plant-level analytical grain
- Philippine fuel-mix findings in this project are primarily based on installed capacity, not actual generation share

---

## Repository Structure

The repository is organized into the following major components:

- `notebooks/` — reference integration prototype and country-level analytical/modeling notebooks
- `data/raw/` — source-faithful ingested data
- `data/staging/` — cleaned and standardized source-specific datasets
- `data/curated/` — validated integrated analytical datasets
- `src/extract/` — automated source-ingestion components
- `src/transform/` — production transformation and integration modules
- `src/validate/` — reusable data-quality validation logic
- `src/load/` — partitioning and PostgreSQL-loading components
- `dags/` — Apache Airflow DAG definitions
- `sql/` — PostgreSQL schemas and analytical queries
- `tests/` — automated regression and component tests
- `config/` — project configuration
- `logs/` — generated execution logs
- `docs/` — architecture, profiling, integration, analysis, and project documentation
- `outputs/` — generated reports and analytical outputs

Generated RAW, STAGING, CURATED, log, and output files are excluded from normal Git tracking where appropriate.

---

## Data Architecture

The production pipeline follows the layered architecture:

**RAW → STAGING → CURATED → POSTGRESQL**

### RAW Layer

Contains source-faithful data retrieved from the approved external sources.

No analytical joins are performed in this layer.

### STAGING Layer

Contains cleaned and standardized source-specific datasets prepared for integration.

Typical staging operations include:

- type conversion
- string cleaning
- ISO-code normalization
- year filtering
- required-field handling
- source-specific cleaning
- removal of unnecessary or overlapping fields
- creation of one-record-per-country snapshots where required

### CURATED Layer

Contains the validated plant-level analytical dataset created through integration of the staging-layer sources.

The final curated analytical grain remains:

**ONE ROW = ONE REAL POWER PLANT**

The principal curated dataset is:

`data/curated/eta_curated_2019.parquet`

### PostgreSQL Layer

The wide curated analytical dataset is normalized into seven relational tables:

- `countries`
- `fuel_types`
- `power_plants`
- `plant_generation`
- `country_emissions`
- `country_economic_indicators`
- `country_fuel_capacity`

This representation supports relational integrity, SQL retrieval, and structured analytical access.

---

## Production Transformation Flow

The implemented production flow is:

**Source Ingestion → Raw Validation → Staging Transformation → Staging Validation → Curated Integration → Curated Validation → PostgreSQL Loading**

Production transformation entrypoints include:

`python -m src.transform.run_staging`

`python -m src.transform.run_curated`

The PostgreSQL loading entrypoint is:

`python -m src.load.postgres_data_loader`

---

## Transformation Layer

Production transformations are implemented under:

`src/transform/`

The transformation layer includes:

- WRI plant cleaning
- OWID 2019 staging transformation
- World Bank 2019 staging transformation
- installed-capacity feature engineering
- three-source integration
- RAW → STAGING orchestration
- STAGING → CURATED orchestration

The reference notebook is no longer required to execute the production transformation pipeline.

---

## PostgreSQL Implementation

The PostgreSQL implementation includes:

- normalized schema definition
- primary-key relationships
- foreign-key relationships
- bulk data loading
- UPSERT behavior
- repeatable loading
- relationship-integrity verification
- representative analytical queries

The validated PostgreSQL load contains:

| Table | Rows |
|---|---:|
| `countries` | 167 |
| `fuel_types` | 15 |
| `power_plants` | 34,936 |
| `plant_generation` | 193,976 |
| `country_emissions` | 164 |
| `country_economic_indicators` | 162 |
| `country_fuel_capacity` | 698 |

The PostgreSQL loader was executed repeatedly with unchanged row counts, demonstrating idempotent loading.

Relationship-integrity checks returned zero orphan rows for the implemented foreign-key relationships.

---

## Partitioning and File Formats

The repository includes utilities for:

- CSV, JSON, and Parquet format comparison
- Hive-style Parquet partitioning by country
- selective partition reads
- file-pruning comparison
- rerun-safe partition writes

The current partitioning demonstration uses the WRI plant table and partitions records by ISO-3 country code.

The partitioning utility can also be applied to compatible plant-level datasets containing the required partition key.

Partitioning documentation is maintained under:

`docs/file_formats/`

---

## Validation Approach

The project uses automated validation across multiple pipeline stages.

Validation areas include:

- required-column checks
- data-type checks
- nullability checks
- uniqueness checks
- duplicate-row checks
- ISO-code format checks
- accepted-value checks
- numerical-range checks
- row-count sanity checks
- referential-integrity checks
- plant-grain preservation
- Philippines-preservation checks
- source-match consistency checks

The validation framework is maintained under:

`src/validate/`

Validation reports and logs are generated during execution where applicable.

---

## Logging and Error Handling

Pipeline components use Python logging and explicit exception handling.

Examples include:

- ingestion logging with UTC batch metadata
- download and HTTP error handling
- source-specific staging failure reporting
- curated-transformation exception logging
- validation PASS/WARN/FAIL reporting
- PostgreSQL transaction rollback on load failure

Generated runtime logs are stored outside normal Git history.

---

## Secrets and Configuration

Environment-specific credentials and secrets are not intended to be committed to the repository.

The project includes:

`.env.example`

as a template for local configuration.

The actual:

`.env`

file is excluded through `.gitignore`.

The repository also excludes common credential, private-key, secret, and virtual-environment files.

---

## Docker Environment

Docker Compose provides the reproducible service environment used by the project.

The Docker environment supports:

- PostgreSQL
- Apache Airflow
- pipeline execution containers
- shared project data and output mounts

The PostgreSQL schema and complete normalized load have been successfully executed inside the Dockerized environment.

---

## Apache Airflow Orchestration

The intended Airflow task sequence is:

```text
start
  ↓
extract_all
  ↓
validate_raw
  ↓
transform_staging
  ↓
validate_staging
  ↓
transform_curated
  ↓
validate_curated
  ↓
load_postgres
  ↓
end