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

The production pipeline programmatically collects data from three independent sources, preserves source-faithful raw inputs, cleans and validates each source, integrates the data at plant-level grain, stores normalized outputs in PostgreSQL, and orchestrates the end-to-end workflow with Apache Airflow inside Docker.

The project also supports a separate country-level analytical extension for clustering, Philippine benchmarking, exploratory modeling, and hypothetical installed-capacity transition scenarios. This analytical layer uses the validated curated dataset as its input and does not change the production grain.

---

## Problem Statement

Countries need to reduce carbon emissions, but they rely on very different mixes of coal, gas, oil, and renewable energy. This makes it difficult to identify which countries face similar power-generation challenges and how their installed-capacity structures differ.

The information needed to study these patterns is also distributed across independent data sources. The Global Power Plant Database provides plant-level infrastructure and capacity information, Our World in Data provides national emissions indicators, and the World Bank provides economic and demographic indicators. These sources differ in format, analytical grain, naming conventions, coverage, and acquisition method.

A one-time manual merge would be difficult to reproduce, validate, maintain, and rerun. This project therefore builds an automated data-engineering pipeline that retrieves, validates, transforms, and integrates the sources while preserving the production grain of one row per real power plant.

The resulting data foundation is used to group countries with similar energy profiles, compare the Philippines with economically comparable countries, and explore hypothetical changes in installed-capacity composition.

The project provides comparative analytical support rather than policy prescriptions. Installed capacity is not equivalent to actual electricity generation, national CO2 emissions include activity beyond the power sector, and the 2019 cross-sectional analysis does not establish causality or prove temporal economic-emissions decoupling.

---

## Stakeholders and Intended Users

The intended stakeholders and users of the project include:

- energy and sustainability researchers who need integrated power-plant, emissions, and economic data
- data analysts who need a reproducible dataset for cross-country comparison
- decision-support users who want to examine national energy-transition patterns and comparable country profiles
- Philippine-focused analysts who want to benchmark the country's installed-capacity structure against countries with similar economic and energy conditions
- technical users who need a reproducible, auditable, and rerunnable data pipeline rather than a one-time spreadsheet merge
- course evaluators and future maintainers who need clear documentation, validation evidence, and traceable engineering decisions

The project is intended to support comparative analysis and technical exploration. Its outputs should not be interpreted as direct national energy-policy recommendations.

---

## Project Objectives

The project aims to:

1. Build a reproducible data-engineering pipeline that programmatically retrieves and integrates the Global Power Plant Database, Our World in Data CO2 and greenhouse-gas data, and selected World Bank indicators.
2. Preserve source-faithful inputs and organize data through clearly separated RAW, STAGING, and CURATED layers.
3. Maintain the production grain of one row per real power plant while enriching plant records with applicable 2019 country-level emissions, economic, and demographic indicators using ISO-3 country codes.
4. Implement automated data-quality checks covering schema, data types, nullability, uniqueness, accepted values, numerical ranges, referential integrity, source coverage, and preservation of the intended grain.
5. Store the validated integrated data in a normalized PostgreSQL schema with repeatable and idempotent loading behavior.
6. Orchestrate the complete workflow with Apache Airflow inside a reproducible Docker environment.
7. Create a separate country-level analytical dataset for clustering countries by energy, carbon-intensity, and economic characteristics.
8. Compare the Philippines with countries that have broadly similar economic and energy conditions but different installed-capacity structures.
9. Explore hypothetical Philippine coal-to-renewable installed-capacity shifts without presenting them as forecasts of actual generation, policy feasibility, or causal emissions reduction.
10. Produce documented, testable, and reusable outputs that can support future extensions such as longitudinal decoupling analysis.

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

The Global Power Plant Database is the base dataset for the production integration.

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

The World Bank indicator codes used are:

- `NY.GDP.MKTP.CD`
- `SP.POP.TOTL`
- `NY.GDP.PCAP.CD`

The three sources are integrated primarily through ISO-3 country codes.

---

## Reference Integration Prototype

The validated three-source reference prototype is stored in:

`notebooks/01_merge_prototype.ipynb`

The notebook integrates:

**Global Power Plant Database + OWID 2019 indicators + World Bank 2019 indicators**

The Global Power Plant Database remains the base dataset.

The natural analytical grain of the final integrated production dataset is:

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
- Country-level installed-capacity features are joined back to plant-level records without changing the final production grain.

Detailed integration assumptions are documented in:

`docs/integration/integration_rules.md`

---

## Validated Integrated Dataset Characteristics

The validated three-source production output reproduces the following plant-level characteristics:

- 34,936 plant rows
- 34,936 unique `gppd_idnr` values
- 167 countries
- 123 Philippine plant rows
- 34,927 OWID-matched plant rows
- 34,886 World Bank-matched plant rows
- 0 duplicate plant IDs

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

The completed data-engineering pipeline supports a separate country-level analytical extension available in:

`notebooks/02_country_clustering_philippines_analysis.ipynb`

The notebook transforms the validated plant-level curated dataset into a country-level analytical dataset with the grain:

**ONE ROW = ONE COUNTRY**

The analysis addresses the question:

**Which countries have cleaner energy profiles and lower carbon emissions, and how does the Philippines compare with countries with similar energy and economic conditions?**

### Analytical Approach

The notebook includes:

- country-level aggregation of installed-capacity, emissions, and economic indicators
- K-Means clustering using selected energy, carbon-intensity, and economic characteristics
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
- GDP per capita of approximately US$3,401

The Philippine profile is not identical to the Cluster 4 average. The Philippines has a higher renewable share and lower coal share than the average country in its cluster.

### Cleaner Installed-Capacity Benchmarks

Using same-cluster membership, economic comparability, higher renewable share, lower fossil share, and lower coal share as transparent comparison criteria, the analysis identifies:

- Morocco
- Laos
- Vietnam

as potential cleaner installed-capacity benchmarks for the Philippines.

These countries should be interpreted as comparative energy-transition references rather than models that the Philippines should directly copy.

None of the selected benchmarks has both lower CO2 per capita and lower CO2 per GDP than the Philippines. The comparison therefore highlights differences in **installed-capacity structure**, not proof that a cleaner installed-capacity mix automatically produces lower national emissions.

### Philippine Capacity-Shift Scenarios

The notebook evaluates hypothetical changes to the Philippine installed-capacity mix by reallocating:

- 5 percentage points
- 10 percentage points
- 20 percentage points

from coal installed capacity toward renewable installed capacity while keeping total installed capacity constant.

These scenarios illustrate changes in capacity composition only.

They are not forecasts of actual electricity generation, construction schedules, retirements, grid constraints, costs, policy feasibility, or causal future emissions reductions.

### Analytical Limitations

The analysis uses a cross-sectional 2019 snapshot and is exploratory rather than causal.

Additional limitations include:

- installed capacity is not equivalent to actual electricity generation
- national CO2 indicators include economic activity beyond the electricity sector
- countries differ in geography, resources, electricity demand, industrial structure, grid conditions, and policy
- some countries were excluded from clustering because of missing analytical variables
- K-Means produces exploratory distance-based groupings rather than definitive country classifications
- predictive models show associations and should not be interpreted as causal emissions models
- true economic-emissions decoupling requires longitudinal multi-year analysis

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
- generation data are not required to preserve the plant-level production grain
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

**External Sources → RAW → STAGING → CURATED → PostgreSQL**

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

The final curated production grain remains:

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

```bash
python -m src.transform.run_staging
python -m src.transform.run_curated
```

The PostgreSQL loading entrypoint is:

```bash
python -m src.load.postgres_data_loader
```

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
- check constraints and indexes
- bulk data loading
- UPSERT behavior
- transactional loading
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

The PostgreSQL loader was executed repeatedly with unchanged row counts, demonstrating idempotent loading under the same input.

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
- Airflow task-state and retry visibility

Generated runtime logs are stored outside normal Git history.

---

## Installation and Prerequisites

### Required Software

Install the following before running the project:

- Git
- Docker Desktop, or Docker Engine with Docker Compose v2
- Python 3.11 or a compatible Python 3 environment for local utilities and tests

Verify the tools:

```bash
git --version
docker --version
docker compose version
python --version
```

### Clone the Repository

```bash
git clone https://github.com/Sophia-A04/DSS150P-GroupEta-ProjectPipeline.git
cd DSS150P-GroupEta-ProjectPipeline
```

### Optional Local Python Environment

Docker is the primary reproducible runtime. If you also want to run project modules or tests directly on the host machine, create and activate a virtual environment.

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Secrets and Environment Configuration

The repository includes:

`.env.example`

as the environment-variable template.

Create the local `.env` file before starting Docker.

macOS/Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The template contains PostgreSQL and Airflow settings such as:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
AIRFLOW_DB
AIRFLOW_USER
AIRFLOW_PASSWORD
AIRFLOW_EMAIL
AIRFLOW_FERNET_KEY
AIRFLOW_SECRET_KEY
```

Change the placeholder passwords and secrets before starting the environment.

### Generate a Real Airflow Fernet Key

Airflow requires a valid Fernet key.

If the local Python environment does not already contain the `cryptography` package, install it:

```bash
python -m pip install cryptography
```

Generate a Fernet key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the generated value into `.env`:

```text
AIRFLOW_FERNET_KEY=<generated-key>
```

A random Airflow webserver secret can also be generated with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the result into:

```text
AIRFLOW_SECRET_KEY=<generated-secret>
```

The actual `.env` file is excluded through `.gitignore`.

Do not commit real passwords, Fernet keys, API keys, private keys, or other secrets.

---

## Docker Environment

Docker Compose provides the reproducible runtime for:

- PostgreSQL
- Apache Airflow initialization
- Apache Airflow webserver
- Apache Airflow scheduler
- one-shot/manual project pipeline execution
- shared project data, log, SQL, and output mounts

### Start the Environment

Build the images and start the services in the foreground:

```bash
docker compose up --build
```

To run the long-lived services in the background:

```bash
docker compose up -d --build
```

Check service status:

```bash
docker compose ps
```

### Stop the Environment

Stop and remove the containers and project network while preserving the named PostgreSQL data volume:

```bash
docker compose down
```

Do not routinely run:

```bash
docker compose down -v
```

The `-v` flag deletes the named PostgreSQL volume and therefore destroys the persisted PostgreSQL data. Use it only when a full database reset is intentionally required.

---

## PostgreSQL Initialization

PostgreSQL initialization occurs in two distinct stages.

### 1. Docker Database Initialization

The `postgres` service uses the official PostgreSQL 15 image.

On the first startup of a new PostgreSQL volume:

1. the official image creates the database defined by `POSTGRES_DB`
2. the project mounts `config/postgres/init-multiple-dbs.sh` into `/docker-entrypoint-initdb.d/`
3. the script reads `POSTGRES_MULTIPLE_DATABASES`
4. the script creates additional databases that do not already exist, including the separate Airflow metadata database configured by `AIRFLOW_DB`

The initialization script runs when PostgreSQL creates a new data directory. It is not intended to recreate the databases on every normal container restart.

### 2. Project Schema Initialization and Curated Data Load

The project relational schema is defined in:

`sql/schema.sql`

The schema contains the seven normalized project tables:

- `countries`
- `fuel_types`
- `power_plants`
- `plant_generation`
- `country_emissions`
- `country_economic_indicators`
- `country_fuel_capacity`

The project schema is applied by the PostgreSQL loader, not by the PostgreSQL container initialization script.

During the Airflow pipeline, the `load_postgres` task executes:

```bash
python -m src.load.postgres_data_loader
```

The loader:

1. connects to the project PostgreSQL database
2. applies `sql/schema.sql`
3. reads `data/curated/eta_curated_2019.parquet`
4. normalizes the curated data into the seven project tables
5. loads the rows using UPSERT behavior
6. commits on success or rolls back on failure

To initialize or verify only the project schema manually:

```bash
docker compose run --rm pipeline python -m src.load.postgres_loader
```

To run the full PostgreSQL schema-and-data load manually after the curated dataset exists:

```bash
docker compose run --rm pipeline python -m src.load.postgres_data_loader
```

---

## Apache Airflow Orchestration

The Airflow DAG is:

`energy_pipeline`

The task sequence is:

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
```

The DAG is configured with:

- schedule: daily at `02:00 UTC`
- `catchup=False`
- `max_active_runs=1`
- default retries: 2 with a 2-minute delay
- no retries for validation tasks
- one retry for staging transformation, curated transformation, and PostgreSQL loading

Airflow manages task ordering, retries, task states, and runtime logs. Docker provides the runtime environment; Airflow provides workflow orchestration.

---

## Using the Airflow Web Interface

After the Docker services are running, open:

`http://localhost:8080`

Log in using the values configured in `.env`:

- username: `AIRFLOW_USER`
- password: `AIRFLOW_PASSWORD`

### Trigger the Pipeline Manually

1. Open the Airflow web interface.
2. Locate the DAG named `energy_pipeline`.
3. Unpause the DAG if it is paused.
4. Open the DAG.
5. Select **Trigger DAG**.
6. Monitor the run using the Grid or Graph view.
7. Wait for the tasks to proceed from `extract_all` through `load_postgres` and `end`.

### View Task Logs

To inspect a task:

1. open the `energy_pipeline` DAG
2. select the relevant DAG run
3. click the task instance
4. select **Logs**

The task log is the primary runtime evidence for diagnosing a failed Airflow task.

A successful end-to-end run executes:

```text
Ingestion
→ RAW validation
→ STAGING transformation
→ STAGING validation
→ CURATED integration
→ CURATED validation
→ PostgreSQL load
```

Repository code shows how the workflow is configured, but actual runtime success should be confirmed through the Airflow UI or runtime logs.

---

## Manual Pipeline Commands

Individual pipeline stages can also be run manually for development or troubleshooting:

```bash
python -m src.extract.run_ingestion
python -m src.validate.raw_validation --source all
python -m src.transform.run_staging
python -m src.validate.staging_validation
python -m src.transform.run_curated
python -m src.validate.integration_validation
python -m src.load.postgres_data_loader
```

Inside the Airflow scheduler container, a task command can be tested directly. For example:

```bash
docker compose exec airflow-scheduler bash -lc "cd /opt/airflow/project && python -m src.load.postgres_data_loader"
```

---

## Testing

The project uses `pytest`.

Run the complete test suite with:

```bash
python -m pytest -q
```

Tests cover areas including:

- reusable data-quality checks
- source discovery and raw validation
- source-specific transformations
- staging validation
- capacity feature engineering
- three-source integration
- curated validation
- CSV, JSON, and Parquet handling
- country partitioning
- PostgreSQL loader behavior

The PostgreSQL loader unit tests do not replace a live Docker/PostgreSQL integration run, so database behavior should also be verified against the running service when needed.

---

## Expected Outputs

The primary generated outputs are:

| Output | Location |
|---|---|
| Source-faithful ingested data | `data/raw/` |
| Cleaned and standardized data | `data/staging/` |
| Integrated curated dataset | `data/curated/eta_curated_2019.parquet` |
| Runtime logs | `logs/` |
| Validation and analytical outputs | `outputs/` |
| PostgreSQL schema | `sql/schema.sql` |
| PostgreSQL analytical queries | `sql/` |
| Philippine context analysis | `sql/philippines_context.sql` |
| Country clustering and Philippine benchmarking notebook | `notebooks/02_country_clustering_philippines_analysis.ipynb` |

Generated RAW, STAGING, CURATED, log, and output artifacts are excluded from normal Git tracking where appropriate.

---

## Troubleshooting

### 1. Confirm the Repository Is Current

```bash
git checkout main
git pull origin main
git status
```

When working on a new fix, create a separate branch rather than editing directly on `main`.

### 2. Check Docker Service Status

```bash
docker compose ps
```

Inspect service logs when needed:

```bash
docker compose logs postgres
docker compose logs airflow-init
docker compose logs airflow-webserver
docker compose logs airflow-scheduler
```

### 3. Airflow UI Does Not Open

Confirm that `airflow-webserver` is running:

```bash
docker compose ps
```

Then inspect:

```bash
docker compose logs airflow-webserver
```

The expected local address is:

`http://localhost:8080`

Also check whether another local application is already using port `8080`.

### 4. PostgreSQL Does Not Start

Inspect the PostgreSQL logs:

```bash
docker compose logs postgres
```

Check whether another local service is already using the configured PostgreSQL host port, normally `5432`.

### 5. Airflow Reports an Invalid Fernet Key

For a fresh setup, confirm that `.env` contains a real Fernet key generated with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Configure the key before initializing Airflow.

Do not casually replace the Fernet key of an already-used Airflow metadata database because existing encrypted values may depend on the previous key.

### 6. DAG Does Not Appear or Does Not Run

Inspect the scheduler logs:

```bash
docker compose logs airflow-scheduler
```

Confirm that the DAG file exists at:

`dags/energy_pipeline_dag.py`

Confirm that the DAG ID shown in the UI is:

`energy_pipeline`

### 7. PostgreSQL Load Cannot Find `schema.sql`

Verify that the SQL directory is mounted inside the Airflow scheduler:

```bash
docker compose exec airflow-scheduler ls -l /opt/airflow/project/sql/schema.sql
```

The expected path is:

`/opt/airflow/project/sql/schema.sql`

If Docker Compose configuration or mounts were changed, recreate the Airflow services:

```bash
docker compose up -d --force-recreate airflow-webserver airflow-scheduler
```

### 8. Separate an Airflow Problem from a Python Problem

Run the failing module directly inside the scheduler container.

For the PostgreSQL loader:

```bash
docker compose exec airflow-scheduler bash -lc "cd /opt/airflow/project && python -m src.load.postgres_data_loader"
```

If the command succeeds directly but fails as an Airflow task, investigate orchestration, environment, task configuration, or Airflow runtime logs.

### 9. Check the Upstream Data Layer

Confirm that the required upstream output exists before debugging a downstream stage:

```text
RAW → STAGING → CURATED → PostgreSQL
```

For example, the PostgreSQL loader requires:

`data/curated/eta_curated_2019.parquet`

A downstream failure may be a consequence of an upstream output that was never created.

### 10. Run Validation Before Changing Transformation Logic

Use the appropriate validation command:

```bash
python -m src.validate.raw_validation --source all
python -m src.validate.staging_validation
python -m src.validate.integration_validation
```

Read PASS/WARN/FAIL output before modifying transformation code.

Documented source-coverage warnings should not automatically be treated as pipeline failures.

### 11. Run Automated Tests

For the full suite:

```bash
python -m pytest -q
```

For a localized issue, run the affected test module first, then rerun the full suite.

### 12. Protect the PostgreSQL Volume

For normal troubleshooting, use:

```bash
docker compose down
```

Avoid:

```bash
docker compose down -v
```

unless the PostgreSQL volume is intentionally being deleted and rebuilt.

---

## Known Limitations and Assumptions

Key interpretation limits include:

- installed capacity is not actual electricity generation
- missing generation values do not mean zero generation
- national CO2 emissions include activities beyond electricity generation
- the 2019 cross-sectional analysis does not establish causality
- the current analysis does not demonstrate true longitudinal economic-emissions decoupling
- hypothetical capacity-shift scenarios do not forecast actual construction, retirement, electricity dispatch, grid constraints, storage, costs, reliability, policy feasibility, or future emissions
- Morocco, Laos, and Vietnam are comparative installed-capacity references rather than countries the Philippines should directly copy
- missing national indicators remain null rather than being automatically replaced with zero
- nuclear and other/unclassified fuels are not automatically classified as renewable
- the recorded partitioning performance benchmark applies to the demonstrated WRI plant-table test and should not automatically be generalized to every downstream dataset or environment

---

## Future Improvements

### Longitudinal Decoupling Analysis

The current integrated analysis primarily uses a 2019 cross-sectional snapshot. Future work could integrate multiple years of power-sector, emissions, and economic data to evaluate economic-emissions decoupling over time.

### Improved Electricity-Generation Coverage

Installed capacity does not represent actual electricity generated. Future work could integrate more complete generation data so that installed-capacity structure and actual generation mix can be analyzed separately.

### More Realistic Energy-Transition Scenarios

The current Philippine scenarios mathematically reallocate installed capacity from coal toward renewable sources while keeping total installed capacity constant.

Future scenarios could incorporate:

- electricity demand
- plant construction and retirement schedules
- generation costs
- grid constraints
- storage requirements
- resource availability
- electricity trade
- reliability requirements
- policy constraints

### Configurable Reference Years

The current national enrichment uses a 2019 reference year. Future versions could parameterize the snapshot year and create comparable outputs for multiple periods.

### Stronger Database Integration Testing

A future CI workflow could start a temporary PostgreSQL service and execute the full schema and loader process as an automated integration test.

### Expanded Analytical Validation

Future analytical work could compare alternative clustering methods, perform cluster-stability analysis, and evaluate modeling approaches that reduce the multicollinearity among installed-capacity-share predictors.

### Additional Operational Improvements

Future engineering work could add:

- automated CI checks for the full Dockerized workflow
- configurable pipeline parameters
- richer data-lineage metadata
- automated data-freshness reporting
- additional monitoring and alerting for failed scheduled runs

---

## Reproducibility and Safety Notes

- Keep the real `.env` file out of version control.
- Use `main` as the integration branch and perform changes through focused branches and pull requests.
- Treat generated RAW, STAGING, CURATED, log, and output artifacts according to the repository's `.gitignore` rules.
- Preserve the production grain of one row per real power plant.
- Use ISO-3 as the primary country integration key.
- Do not interpret missing values as zero.
- Do not describe installed-capacity shares as actual electricity-generation shares.
- Do not interpret the 2019 analytical extension as causal proof of decoupling.
- Do not use `docker compose down -v` unless destroying the PostgreSQL data volume is intentional.
