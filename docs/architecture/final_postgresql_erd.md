# Final PostgreSQL Entity-Relationship Diagram

## Purpose

This document presents the final PostgreSQL relational model implemented for Group Eta's data engineering pipeline.

The model normalizes the wide curated analytical dataset into seven relational tables while preserving the curated Parquet dataset separately for analytical use.

---

## Final ERD

```mermaid
erDiagram

    COUNTRIES ||--o{ POWER_PLANTS : contains
    COUNTRIES ||--o{ COUNTRY_EMISSIONS : has
    COUNTRIES ||--o{ COUNTRY_ECONOMIC_INDICATORS : has
    COUNTRIES ||--o{ COUNTRY_FUEL_CAPACITY : has

    FUEL_TYPES ||--o{ POWER_PLANTS : classifies
    FUEL_TYPES ||--o{ COUNTRY_FUEL_CAPACITY : categorizes

    POWER_PLANTS ||--o{ PLANT_GENERATION : records

    COUNTRIES {
        char3 country_code PK
        text country_name
        text owid_country_name
        text wb_country_name
    }

    FUEL_TYPES {
        smallint fuel_id PK
        varchar fuel_name UK
        varchar fuel_group
    }

    POWER_PLANTS {
        varchar gppd_idnr PK
        char3 country_code FK
        text plant_name
        double capacity_mw
        double latitude
        double longitude
        smallint primary_fuel_id FK
        varchar other_fuel1
        varchar other_fuel2
        varchar other_fuel3
        double commissioning_year
        text owner
        text source
        text source_url
        text geolocation_source
        text wepp_id
        smallint year_of_capacity_data
    }

    PLANT_GENERATION {
        varchar gppd_idnr PK,FK
        smallint generation_year PK
        double generation_gwh
        double estimated_generation_gwh
        text generation_data_source
        text estimation_note
    }

    COUNTRY_EMISSIONS {
        char3 country_code PK,FK
        smallint year PK
        double co2
        double co2_per_capita
        double coal_co2
        double gas_co2
        double oil_co2
        double methane
        double nitrous_oxide
        double total_ghg
        double primary_energy_consumption
        double share_global_co2
    }

    COUNTRY_ECONOMIC_INDICATORS {
        char3 country_code PK,FK
        smallint year PK
        numeric gdp_current_usd
        bigint population
        numeric gdp_per_capita_current_usd
    }

    COUNTRY_FUEL_CAPACITY {
        char3 country_code PK,FK
        smallint fuel_id PK,FK
        smallint snapshot_year PK
        integer plant_count
        double installed_capacity_mw
        double capacity_share_pct
    }