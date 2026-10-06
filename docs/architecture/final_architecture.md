# Final System Architecture

## Overview

Group Eta's project implements a reproducible data engineering pipeline integrating three approved data sources:

- WRI Global Power Plant Database
- Our World in Data CO2 and Greenhouse Gas Emissions Dataset
- World Bank Indicators API

The system follows a layered architecture:

RAW → STAGING → CURATED → POSTGRESQL

Apache Airflow provides pipeline orchestration, while Docker Compose provides the reproducible execution environment.

---

## Architecture Diagram

```mermaid
flowchart TB

    subgraph SOURCES["External Data Sources"]
        WRI["WRI Global Power Plant Database"]
        OWID["OWID CO2 Dataset"]
        WB["World Bank Indicators API"]
    end

    subgraph EXTRACT["Extraction Layer"]
        INGEST["Python Ingestion Modules<br/>src/extract/"]
    end

    subgraph RAW["RAW Layer"]
        RWRI["WRI Raw Data"]
        ROWID["OWID Raw Data"]
        RWB["World Bank Raw Data"]
    end

    subgraph VALIDATION1["Raw Validation"]
        RAWVAL["Automated Raw Data Validation<br/>src/validate/"]
    end

    subgraph STAGING["STAGING Layer"]
        SWRI["Cleaned WRI Plants"]
        SOWID["OWID 2019 Snapshot"]
        SWB["World Bank 2019 Snapshot"]
    end

    subgraph VALIDATION2["Staging Validation"]
        STGVAL["Schema, Type, Range,<br/>Uniqueness and ISO Checks"]
    end

    subgraph TRANSFORM["Transformation + Integration"]
        CAP["Installed Capacity<br/>Feature Engineering"]
        INTEGRATE["Three-Source Integration"]
    end

    subgraph CURATED["CURATED Layer"]
        CUR["eta_curated_2019.parquet<br/>34,936 plant rows"]
    end

    subgraph VALIDATION3["Curated Validation"]
        CURVAL["Integration + Data Quality Validation"]
    end

    subgraph STORAGE["Structured Storage"]
        PG["PostgreSQL"]
        TABLES["7 Normalized Tables"]
    end

    subgraph OUTPUTS["Analytical / Documentation Outputs"]
        SQL["Representative SQL Queries"]
        PHL["Philippines Context Analysis"]
        PART["Partitioned / File-Format Outputs"]
    end

    subgraph ORCHESTRATION["Orchestration + Runtime"]
        AF["Apache Airflow"]
        DK["Docker Compose"]
    end

    WRI --> INGEST
    OWID --> INGEST
    WB --> INGEST

    INGEST --> RWRI
    INGEST --> ROWID
    INGEST --> RWB

    RWRI --> RAWVAL
    ROWID --> RAWVAL
    RWB --> RAWVAL

    RAWVAL --> SWRI
    RAWVAL --> SOWID
    RAWVAL --> SWB

    SWRI --> STGVAL
    SOWID --> STGVAL
    SWB --> STGVAL

    STGVAL --> CAP
    CAP --> INTEGRATE
    SOWID --> INTEGRATE
    SWB --> INTEGRATE

    INTEGRATE --> CUR
    CUR --> CURVAL

    CURVAL --> PG
    PG --> TABLES

    CUR --> PART
    TABLES --> SQL
    TABLES --> PHL

    AF -. orchestrates .-> INGEST
    AF -. orchestrates .-> RAWVAL
    AF -. orchestrates .-> STGVAL
    AF -. orchestrates .-> INTEGRATE
    AF -. orchestrates .-> CURVAL
    AF -. orchestrates .-> PG

    DK -. provides runtime .-> AF
    DK -. provides runtime .-> PG