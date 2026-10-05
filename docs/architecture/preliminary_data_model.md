# Preliminary PostgreSQL Data Model

## Purpose

This document defines the preliminary relational data model for the Group Eta data engineering project.

The model is based on the current three-source integration design involving:

- Global Power Plant Database (WRI)
- Our World in Data (OWID) CO₂ dataset
- World Bank Indicators API

This document is preliminary and will serve as the basis for the later PostgreSQL schema implementation.

The final PostgreSQL DDL may be refined during the implementation stage.

---

## 1. Modeling Principles

The preliminary model follows these principles:

- Preserve the natural plant-level identity of the Global Power Plant Database.
- Separate plant-level data from country-level data.
- Avoid storing repeated country-level values unnecessarily on every plant row.
- Use ISO-3 country codes as the main country-level relationship key.
- Separate fuel information from plant records where appropriate.
- Represent yearly country indicators using country and year keys.
- Preserve source-specific data while allowing integrated analytical queries.
- Allow later expansion to additional years or indicators.

---

## 2. Main Entities

The preliminary relational model contains the following main entities:

1. `countries`
2. `fuel_types`
3. `power_plants`
4. `plant_generation`
5. `country_emissions`
6. `country_economic_indicators`
7. `country_fuel_capacity`

---

## 3. Countries Table

### Proposed Table Name

`countries`

### Purpose

Stores one record for each country represented in the integrated project data.

### Candidate Primary Key

`country_code`

The value corresponds to the ISO-3 country code used to connect plant-level and country-level datasets.

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| country_code | CHAR(3) | Primary Key | ISO-3 country code |
| country_name | TEXT |  | Standard country name |
| owid_country_name | TEXT |  | Country name used by OWID |
| wb_country_name | TEXT |  | Country name used by World Bank |

### Relationships

One country may contain many power plants.

One country may have multiple yearly emissions records.

One country may have multiple yearly economic indicator records.

One country may have multiple fuel-capacity records.

---

## 4. Fuel Types Table

### Proposed Table Name

`fuel_types`

### Purpose

Stores standardized power plant fuel categories.

### Candidate Primary Key

`fuel_id`

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| fuel_id | SMALLSERIAL | Primary Key | Internal fuel identifier |
| fuel_name | VARCHAR(50) | Unique | Fuel category name |
| fuel_group | VARCHAR(30) |  | Renewable, fossil, or other/unclassified grouping |

### Relationships

One fuel type may be associated with many power plants.

One fuel type may appear in many country-fuel capacity records.

---

## 5. Power Plants Table

### Proposed Table Name

`power_plants`

### Purpose

Stores the primary plant-level records from the Global Power Plant Database.

The natural grain is:

**ONE ROW = ONE REAL POWER PLANT**

### Candidate Primary Key

`gppd_idnr`

This is the candidate plant identifier used in the current reference prototype.

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| gppd_idnr | VARCHAR(50) | Primary Key | Global power plant identifier |
| country_code | CHAR(3) | Foreign Key | References `countries.country_code` |
| plant_name | TEXT |  | Power plant name |
| capacity_mw | DOUBLE PRECISION |  | Installed generation capacity |
| latitude | DOUBLE PRECISION |  | Plant latitude |
| longitude | DOUBLE PRECISION |  | Plant longitude |
| primary_fuel_id | SMALLINT | Foreign Key | References `fuel_types.fuel_id` |
| other_fuel1 | VARCHAR(50) |  | Secondary fuel where available |
| other_fuel2 | VARCHAR(50) |  | Additional fuel where available |
| other_fuel3 | VARCHAR(50) |  | Additional fuel where available |
| commissioning_year | SMALLINT |  | Plant commissioning year |
| owner | TEXT |  | Plant owner |
| source | TEXT |  | Original source |
| source_url | TEXT |  | Source URL |
| geolocation_source | TEXT |  | Geographic data source |
| wepp_id | TEXT |  | WEPP identifier where available |
| year_of_capacity_data | SMALLINT |  | Year associated with reported capacity |

### Foreign Keys

`country_code` → `countries.country_code`

`primary_fuel_id` → `fuel_types.fuel_id`

---

## 6. Plant Generation Table

### Proposed Table Name

`plant_generation`

### Purpose

Stores plant-level electricity-generation observations by year.

This avoids keeping separate repeated columns such as generation for 2013, 2014, 2015, and succeeding years directly in the main plant table.

### Candidate Primary Key

Composite key:

`gppd_idnr + generation_year`

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| gppd_idnr | VARCHAR(50) | Primary Key / Foreign Key | References `power_plants.gppd_idnr` |
| generation_year | SMALLINT | Primary Key | Year of generation observation |
| generation_gwh | DOUBLE PRECISION |  | Reported generation |
| estimated_generation_gwh | DOUBLE PRECISION |  | Estimated generation where applicable |
| generation_data_source | TEXT |  | Generation data source |
| estimation_note | TEXT |  | Estimation methodology or note |

### Relationship

One power plant may have many yearly generation records.

---

## 7. Country Emissions Table

### Proposed Table Name

`country_emissions`

### Purpose

Stores country-level emissions and carbon-related indicators obtained from OWID.

### Candidate Primary Key

Composite key:

`country_code + year`

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| country_code | CHAR(3) | Primary Key / Foreign Key | References `countries.country_code` |
| year | SMALLINT | Primary Key | Observation year |
| co2 | DOUBLE PRECISION |  | CO₂ emissions |
| co2_per_capita | DOUBLE PRECISION |  | CO₂ emissions per capita |
| coal_co2 | DOUBLE PRECISION |  | Coal-related CO₂ |
| gas_co2 | DOUBLE PRECISION |  | Gas-related CO₂ |
| oil_co2 | DOUBLE PRECISION |  | Oil-related CO₂ |
| methane | DOUBLE PRECISION |  | Methane emissions |
| nitrous_oxide | DOUBLE PRECISION |  | Nitrous oxide emissions |
| total_ghg | DOUBLE PRECISION |  | Total greenhouse gas emissions |
| primary_energy_consumption | DOUBLE PRECISION |  | Primary energy consumption |
| share_global_co2 | DOUBLE PRECISION |  | Share of global CO₂ emissions |

Additional OWID fields may be included when required by the final analytical scope.

### Relationship

One country may have many emissions records across different years.

---

## 8. Country Economic Indicators Table

### Proposed Table Name

`country_economic_indicators`

### Purpose

Stores country-level economic and demographic indicators from the World Bank.

### Candidate Primary Key

Composite key:

`country_code + year`

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| country_code | CHAR(3) | Primary Key / Foreign Key | References `countries.country_code` |
| year | SMALLINT | Primary Key | Observation year |
| gdp_current_usd | NUMERIC(24,2) |  | GDP in current US dollars |
| population | BIGINT |  | Total population |
| gdp_per_capita_current_usd | NUMERIC(18,4) |  | GDP per capita in current US dollars |

### Relationship

One country may have many economic indicator records across different years.

---

## 9. Country Fuel Capacity Table

### Proposed Table Name

`country_fuel_capacity`

### Purpose

Stores derived country-level installed-capacity statistics by fuel category.

### Candidate Primary Key

Composite key:

`country_code + fuel_id`

A snapshot year or run identifier may later be added to the key if multiple capacity snapshots are stored.

### Preliminary Fields

| Field | Proposed PostgreSQL Type | Key | Description |
|---|---|---|---|
| country_code | CHAR(3) | Primary Key / Foreign Key | References `countries.country_code` |
| fuel_id | SMALLINT | Primary Key / Foreign Key | References `fuel_types.fuel_id` |
| plant_count | INTEGER |  | Number of plants using the fuel |
| installed_capacity_mw | DOUBLE PRECISION |  | Total installed capacity for the fuel |
| capacity_share_pct | DOUBLE PRECISION |  | Share of national installed capacity |

### Relationships

One country may have many fuel-capacity records.

One fuel type may appear in many countries.

This table therefore resolves a many-to-many analytical relationship between countries and fuel categories.

---

## 10. Proposed Relationships

The preliminary relationships are:

`countries` 1 → many `power_plants`

`fuel_types` 1 → many `power_plants`

`power_plants` 1 → many `plant_generation`

`countries` 1 → many `country_emissions`

`countries` 1 → many `country_economic_indicators`

`countries` 1 → many `country_fuel_capacity`

`fuel_types` 1 → many `country_fuel_capacity`

---

## 11. Candidate Keys Summary

| Table | Candidate Primary Key |
|---|---|
| countries | `country_code` |
| fuel_types | `fuel_id` |
| power_plants | `gppd_idnr` |
| plant_generation | (`gppd_idnr`, `generation_year`) |
| country_emissions | (`country_code`, `year`) |
| country_economic_indicators | (`country_code`, `year`) |
| country_fuel_capacity | (`country_code`, `fuel_id`) |

---

## 12. Preliminary Foreign Keys

| Child Table | Foreign Key | Parent Table |
|---|---|---|
| power_plants | `country_code` | countries |
| power_plants | `primary_fuel_id` | fuel_types |
| plant_generation | `gppd_idnr` | power_plants |
| country_emissions | `country_code` | countries |
| country_economic_indicators | `country_code` | countries |
| country_fuel_capacity | `country_code` | countries |
| country_fuel_capacity | `fuel_id` | fuel_types |

---

## 13. Normalization Rationale

The integrated reference CSV contains plant-level information together with repeated country-level information.

For analytical export, this wide structure is useful.

For PostgreSQL storage, however, repeatedly storing the same country-level values for every plant would introduce unnecessary duplication.

The preliminary relational model therefore separates:

- plant-level data
- country information
- fuel information
- yearly emissions indicators
- yearly economic indicators
- yearly or snapshot-derived generation/capacity information

The wide curated dataset may still be maintained as an analytical output even when the PostgreSQL database uses a more normalized relational structure.

---

## 14. Current Scope

This document represents a preliminary design only.

It does not yet define:

- Final SQL DDL syntax
- Final indexes
- Final CHECK constraints
- Final nullability rules
- Final cascading behavior
- Final database-loading logic
- Performance optimization
- Final physical partitioning

These will be refined during the PostgreSQL implementation stage.

---

## 15. Next Modeling Step

The next design artifact will be a preliminary Entity-Relationship Diagram (ERD) showing the relationships between:

- Countries
- Power plants
- Fuel types
- Plant generation
- Country emissions
- Country economic indicators
- Country fuel capacity

The final ERD may be revised once the modular transformation and PostgreSQL implementation are completed.