# Data Dictionary — Curated Integrated Dataset

**Project:** DSS150P Group Eta — Data Engineering Pipeline
**Dataset:** `eta_curated_2019.parquet`
**Location:** `data/curated/eta_curated_2019.parquet`
**Producer:** `src/transform/run_curated.py` → `integrate_sources.build_curated_dataset()`
**Validation:** `python -m src.validate.integration_validation` → 24 checks, 0 errors, 1 warning
**Consumers:** PostgreSQL loader (`src/load/`), analytics layer, presentation / technical defense

## Grain

One row = one real power plant. Row count is 34,936 and matches the WRI raw plant count exactly. The primary key is `gppd_idnr` (unique = 34,936).

Country-level indicators (OWID CO₂, World Bank GDP/population) are attached by a many-to-one left join on ISO-3 country code. Unmatched countries are retained; their country-level fields are null rather than dropped, so the plant-level grain is never broken.

## Schema (162 columns)

Every value in the Type, Nulls, Unique, and Example columns below is taken from the live profile of `eta_curated_2019.parquet`.

### A. Plant identity and location (from WRI)

| Field | Type | Nulls | Unique | Description | Example |
|---|---|---|---|---|---|
| `gppd_idnr` | string | 0 | 34,936 | WRI/GPPD plant identifier; primary key | `GEODB0040538` |
| `name` | string | 0 | 34,528 | Plant name as reported by WRI | `Kajaki Hydroelectric Power Plant Afghanistan` |
| `country` | string | 0 | 167 | ISO-3 country code of the plant; join key to OWID and World Bank | `AFG` |
| `country_long` | string | 0 | 167 | Full country name | `Afghanistan` |
| `latitude` | float64 | 0 | 31,779 | Plant latitude, WGS-84 | `32.322` |
| `longitude` | float64 | 0 | 33,036 | Plant longitude, WGS-84 | `65.119` |

### B. Capacity and fuel (from WRI)

| Field | Type | Nulls | Description | Example |
|---|---|---|---|---|
| `capacity_mw` | float64 | 0 | Installed capacity in MW | `33.0` |
| `primary_fuel` | string | 0 | Primary fuel category (15 distinct values) | `Hydro` |
| `other_fuel1` | string | 32,992 | Secondary fuel if any | `Oil` |
| `other_fuel2` | string | 34,660 | Tertiary fuel if any | `Other` |
| `other_fuel3` | string | 34,844 | Quaternary fuel if any | `Other` |
| `commissioning_year` | float64 | 17,489 | Year plant began operating | `1965.0` |
| `owner` | string | 14,068 | Owner name; source-faithful, some entries carry CSV encoding artifacts | `SociÃ©te AlgÃ©rienne de Production de l'Electricité` |
| `source` | string | 15 | WRI source attribution for the plant record | `GEODB` |
| `url` | string | 18 | Source URL for the plant record | `http://globalenergyobservatory.org` |
| `geolocation_source` | string | 419 | Source of the coordinates | `GEODB` |
| `wepp_id` | string | 18,702 | WEPP database identifier | `1009793` |
| `year_of_capacity_data` | float64 | 20,049 | Year the capacity figure refers to | `2017.0` |

### C. Historical generation (from WRI, 2013–2019)

| Field | Type | Nulls | Example |
|---|---|---|---|
| `generation_gwh_2013` | float64 | 28,519 | `89.59527777777778` |
| `generation_gwh_2014` | float64 | 27,710 | `102.64277777777778` |
| `generation_gwh_2015` | float64 | 26,733 | `96.55555555555556` |
| `generation_gwh_2016` | float64 | 25,792 | `95.87277777777778` |
| `generation_gwh_2017` | float64 | 25,436 | `85.90027777777777` |
| `generation_gwh_2018` | float64 | 25,299 | `92.68222222222222` |
| `generation_gwh_2019` | float64 | 25,277 | `2.467` |
| `generation_data_source` | string | 23,536 | `Australia Clean Energy Regulator` |
| `estimated_generation_gwh_2013` | float64 | 18,816 | `123.77` |
| `estimated_generation_gwh_2014` | float64 | 18,433 | `162.9` |
| `estimated_generation_gwh_2015` | float64 | 17,886 | `97.39` |
| `estimated_generation_gwh_2016` | float64 | 17,366 | `137.76` |
| `estimated_generation_gwh_2017` | float64 | 1,798 | `119.5` |
| `estimated_generation_note_2013` | string | 0 | `HYDRO-V1` |
| `estimated_generation_note_2014` | string | 0 | `HYDRO-V1` |
| `estimated_generation_note_2015` | string | 0 | `HYDRO-V1` |
| `estimated_generation_note_2016` | string | 0 | `HYDRO-V1` |
| `estimated_generation_note_2017` | string | 0 | `HYDRO-V1` |

`generation_gwh_2019` may contain negative values. This is a source-side issue and is classified as a warning by raw WRI validation, not an error. See `docs/known_issues.md`.

### D. Derived capacity features

Produced by `src/transform/capacity_features.py`.

| Field | Type | Nulls | Description | Example |
|---|---|---|---|---|
| `total_plant_count` | int64 | 0 | Plants in the same country / primary-fuel group | `9` |
| `total_installed_capacity_mw` | float64 | 0 | Total installed capacity for the plant's country | `300.55` |
| `Biomass_capacity_mw` | float64 | 0 | Biomass capacity in the country, MW | `0.0` |
| `Coal_capacity_mw` | float64 | 0 | Coal capacity in the country, MW | `0.0` |
| `Cogeneration_capacity_mw` | float64 | 0 | Cogeneration capacity in the country, MW | `0.0` |
| `Gas_capacity_mw` | float64 | 0 | Gas capacity in the country, MW | `42.0` |
| `Geothermal_capacity_mw` | float64 | 0 | Geothermal capacity in the country, MW | `0.0` |
| `Hydro_capacity_mw` | float64 | 0 | Hydro capacity in the country, MW | `238.55` |
| `Nuclear_capacity_mw` | float64 | 0 | Nuclear capacity in the country, MW | `0.0` |
| `Oil_capacity_mw` | float64 | 0 | Oil capacity in the country, MW | `0.0` |
| `Other_capacity_mw` | float64 | 0 | Other capacity in the country, MW | `0.0` |
| `Petcoke_capacity_mw` | float64 | 0 | Petcoke capacity in the country, MW | `0.0` |
| `Solar_capacity_mw` | float64 | 0 | Solar capacity in the country, MW | `20.0` |
| `Storage_capacity_mw` | float64 | 0 | Storage capacity in the country, MW | `0.0` |
| `Waste_capacity_mw` | float64 | 0 | Waste capacity in the country, MW | `0.0` |
| `Wave and Tidal_capacity_mw` | float64 | 0 | Wave and tidal capacity in the country, MW | `0.0` |
| `Wind_capacity_mw` | float64 | 0 | Wind capacity in the country, MW | `0.0` |
| `Biomass_share_pct` | float64 | 0 | Biomass share of the country total, percent | `0.0` |
| `Coal_share_pct` | float64 | 0 | Coal share of the country total, percent | `0.0` |
| `Cogeneration_share_pct` | float64 | 0 | Cogeneration share of the country total, percent | `0.0` |
| `Gas_share_pct` | float64 | 0 | Gas share of the country total, percent | `13.974380302778238` |
| `Geothermal_share_pct` | float64 | 0 | Geothermal share of the country total, percent | `0.0` |
| `Hydro_share_pct` | float64 | 0 | Hydro share of the country total, percent | `79.37115288637499` |
| `Nuclear_share_pct` | float64 | 0 | Nuclear share of the country total, percent | `0.0` |
| `Oil_share_pct` | float64 | 0 | Oil share of the country total, percent | `0.0` |
| `Other_share_pct` | float64 | 0 | Other share of the country total, percent | `0.0` |
| `Petcoke_share_pct` | float64 | 0 | Petcoke share of the country total, percent | `0.0` |
| `Solar_share_pct` | float64 | 0 | Solar share of the country total, percent | `6.65446681084678` |
| `Storage_share_pct` | float64 | 0 | Storage share of the country total, percent | `0.0` |
| `Waste_share_pct` | float64 | 0 | Waste share of the country total, percent | `0.0` |
| `Wave and Tidal_share_pct` | float64 | 0 | Wave and tidal share of the country total, percent | `0.0` |
| `Wind_share_pct` | float64 | 0 | Wind share of the country total, percent | `0.0` |
| `fossil_capacity_mw` | float64 | 0 | Fossil-fuel group capacity in the country, MW | `42.0` |
| `renewable_capacity_mw` | float64 | 0 | Renewable group capacity in the country, MW | `258.55` |
| `other_or_unclassified_capacity_mw` | float64 | 0 | Other / unclassified group capacity in the country, MW | `0.0` |
| `fossil_share_pct` | float64 | 0 | Fossil group share of the country total, percent | `13.974380302778238` |
| `renewable_share_pct` | float64 | 0 | Renewable group share of the country total, percent | `86.02561969722176` |
| `other_or_unclassified_share_pct` | float64 | 0 | Other / unclassified group share of the country total, percent | `0.0` |
| `country_primary_fuel_plant_count` | int64 | 0 | Plants of the same primary fuel in the country | `6` |
| `country_primary_fuel_capacity_mw` | float64 | 0 | Capacity of the same primary fuel in the country, MW | `238.55` |
| `country_primary_fuel_capacity_share_pct` | float64 | 0 | Share of the same primary fuel within the country, percent | `79.37115288637499` |

### E. OWID 2019 country indicators

Joined on `country` = `iso_code`.

| Field | Type | Nulls | Description | Example |
|---|---|---|---|---|
| `owid_country` | string | 9 | OWID country name | `Afghanistan` |
| `year` | float64 | 9 | Always 2019 | `2019.0` |
| `iso_code` | string | 9 | ISO-3 code | `AFG` |
| `co2` | float64 | 9 | Total CO₂, million tonnes | `10.400110244750977` |
| `co2_per_capita` | float64 | 11 | Tonnes CO₂ per person | `0.2747272849082947` |
| `co2_growth_abs` | float64 | 9 | Year-over-year CO₂ change, million tonnes | `0.2086060047149658` |
| `co2_growth_prct` | float64 | 11 | Year-over-year CO₂ change, percent | `2.0468592643737797` |
| `coal_co2` | float64 | 291 | CO₂ from coal, million tonnes | `3.273106098175049` |
| `gas_co2` | float64 | 546 | CO₂ from gas, million tonnes | `0.2455749958753585` |
| `oil_co2` | float64 | 11 | CO₂ from oil, million tonnes | `6.8431010246276855` |
| `methane` | float64 | 12 | Methane emissions, million tonnes CO₂-equivalent | `15.215601921081545` |
| `nitrous_oxide` | float64 | 12 | Nitrous oxide emissions, million tonnes CO₂-equivalent | `4.597519397735596` |
| `total_ghg` | float64 | 12 | Total greenhouse gases, million tonnes CO₂-equivalent | `36.55088806152344` |
| `primary_energy_consumption` | float64 | 9 | Total primary energy, TWh | `47.11153030395508` |
| `share_global_co2` | float64 | 9 | Country share of global CO₂, percent | `0.0280427951365709` |
| `owid_2019_matched` | bool | 0 | True when the plant's country matched OWID 2019 | `True` |

Additional OWID columns are carried through the many-to-one join unchanged. They include `cement_co2`, `cement_co2_per_capita`, `co2_including_luc`, `co2_including_luc_growth_abs`, `co2_including_luc_growth_prct`, `co2_including_luc_per_capita`, `co2_including_luc_per_gdp`, `co2_including_luc_per_unit_energy`, `co2_per_gdp`, `co2_per_unit_energy`, `coal_co2_per_capita`, `consumption_co2`, `consumption_co2_per_capita`, `consumption_co2_per_gdp`, `cumulative_cement_co2`, `cumulative_co2`, `cumulative_co2_including_luc`, `cumulative_coal_co2`, `cumulative_flaring_co2`, `cumulative_gas_co2`, `cumulative_luc_co2`, `cumulative_oil_co2`, `cumulative_other_co2`, `energy_per_capita`, `energy_per_gdp`, `flaring_co2`, `flaring_co2_per_capita`, `gas_co2_per_capita`, `ghg_excluding_lucf_per_capita`, `ghg_per_capita`, `land_use_change_co2`, `land_use_change_co2_per_capita`, `methane_per_capita`, `nitrous_oxide_per_capita`, `oil_co2_per_capita`, `other_co2_per_capita`, `other_industry_co2`, `share_global_cement_co2`, `share_global_co2_including_luc`, `share_global_coal_co2`, `share_global_cumulative_cement_co2`, `share_global_cumulative_co2`, `share_global_cumulative_co2_including_luc`, `share_global_cumulative_coal_co2`, `share_global_cumulative_flaring_co2`, `share_global_cumulative_gas_co2`, `share_global_cumulative_luc_co2`, `share_global_cumulative_oil_co2`, `share_global_cumulative_other_co2`, `share_global_flaring_co2`, `share_global_gas_co2`, `share_global_luc_co2`, `share_global_oil_co2`, `share_global_other_co2`, `share_of_temperature_change_from_ghg`, `temperature_change_from_ch4`, `temperature_change_from_co2`, `temperature_change_from_ghg`, `temperature_change_from_n2o`, `total_ghg_excluding_lucf`, `trade_co2`, `trade_co2_share`.

### F. World Bank 2019 country indicators

Joined on `country` = `wb_iso_code`.

| Field | Type | Nulls | Description | Example |
|---|---|---|---|---|
| `wb_iso_code` | string | 50 | ISO-3 code | `AFG` |
| `wb_country` | string | 50 | World Bank country name | `Afghanistan` |
| `wb_year` | float64 | 50 | Always 2019 | `2019.0` |
| `wb_gdp_current_usd` | float64 | 90 | GDP, current US$ | `18799444490.1128` |
| `wb_population` | float64 | 50 | Total population | `37856121.0` |
| `wb_gdp_per_capita_current_usd` | float64 | 90 | GDP per capita, current US$ | `496.6025042585` |
| `wb_2019_matched` | bool | 0 | True when the plant's country matched World Bank 2019 | `True` |

`wb_gdp_current_usd` and `wb_gdp_per_capita_current_usd` have more nulls than the match flag. The integrated validator flags 40 rows as WB-matched but with null GDP. See `docs/known_issues.md`.

## Nullability Summary

| Class | Rule | Example fields |
|---|---|---|
| Required | Identity, capacity, plant fuel, and match flags | `gppd_idnr`, `country`, `name`, `capacity_mw`, `primary_fuel`, `owid_2019_matched`, `wb_2019_matched` |
| Optional | Country-level indicators when the plant's country has no match in that source | all OWID and WB value columns |
| Source-faithful | WRI history columns for plants without that year's data | `generation_gwh_2013` through `generation_gwh_2019` |

## Units and Conventions

Capacity is in MW. Generation is in GWh. GHG indicators are in million tonnes of CO₂-equivalent, following OWID convention. GDP is in current US$. Population is in persons. ISO-3 country codes are uppercase and three letters. Share columns are in percent and lie between 0 and 100.

## Provenance

| Source | Type | Role | Retrieval |
|---|---|---|---|
| WRI Global Power Plant Database | CSV | Plant-level base | Raw file, retained as CSV |
| Our World in Data CO₂ dataset | CSV | Country CO₂ and GHG | Raw file, retained as CSV |
| World Bank Indicators API | JSON via REST | Country GDP and population | Programmatic, 2019 slice |
