# Philippines Context Analysis

## Purpose

This analysis summarizes the Philippine records produced by Group Eta's 2019 integrated energy dataset and normalized PostgreSQL database.

The analysis is based on the project's validated WRI power-plant records, OWID emissions indicators, World Bank economic and demographic indicators, and engineered installed-capacity features.

The results describe installed generation capacity and should not be interpreted as electricity-generation shares.

---

## 1. Philippine Power-Plant Summary

The 2019 integrated dataset contains:

- 123 Philippine power plants
- 20,719.30 MW total installed capacity
- 168.45 MW average installed capacity per plant

All 123 Philippine WRI plant records were preserved through the RAW → STAGING → CURATED pipeline and were successfully loaded into PostgreSQL.

---

## 2. Installed Capacity by Primary Fuel

| Primary Fuel | Fuel Group | Plant Count | Installed Capacity (MW) | Capacity Share |
|---|---|---:|---:|---:|
| Coal | Fossil | 23 | 8,731.30 | 42.14% |
| Gas | Fossil | 5 | 3,411.00 | 16.46% |
| Hydro | Renewable | 17 | 3,401.10 | 16.42% |
| Oil | Fossil | 17 | 2,056.10 | 9.92% |
| Geothermal | Renewable | 9 | 1,848.20 | 8.92% |
| Solar | Renewable | 48 | 1,196.40 | 5.77% |
| Wind | Renewable | 2 | 51.90 | 0.25% |
| Biomass | Renewable | 2 | 23.30 | 0.11% |

Coal represents the largest installed-capacity category in the Philippine records at 8,731.30 MW, corresponding to approximately 42.14% of installed capacity.

Gas contributes another 16.46%, while oil contributes 9.92%.

Among renewable sources, hydro has the largest installed capacity at 3,401.10 MW, followed by geothermal at 1,848.20 MW and solar at 1,196.40 MW.

Although solar has the largest plant count among the listed fuel categories, with 48 plants, its installed-capacity share is only 5.77%. This illustrates why plant count alone should not be used as a substitute for installed capacity.

---

## 3. Fossil and Renewable Capacity

The Philippine installed-capacity mix in the integrated dataset is:

| Fuel Group | Plant Count | Installed Capacity (MW) | Installed Capacity Share |
|---|---:|---:|---:|
| Fossil | 45 | 14,198.40 | 68.53% |
| Renewable | 78 | 6,520.90 | 31.47% |

The dataset therefore indicates that approximately 68.53% of Philippine installed capacity is associated with fossil-fuel plants, while approximately 31.47% is associated with renewable plants.

Renewable plants are more numerous in the dataset, but fossil plants account for the larger share of installed capacity.

These values describe installed generation capacity only. They do not measure the amount of electricity actually generated from each fuel source.

---

## 4. Emissions and Economic Context

For the project's 2019 snapshot, the integrated country-level records contain:

- CO2: approximately 142.601
- CO2 per capita: approximately 1.287
- GDP: approximately USD 376.82 billion
- Population: 110,804,683
- GDP per capita: approximately USD 3,400.79

The emissions indicators are sourced from OWID, while GDP, population, and GDP per capita are sourced from the World Bank.

These variables provide national context for interpreting the country's installed power-generation infrastructure.

The current analysis does not claim that the Philippine power-plant capacity mix directly caused the reported national emissions or economic indicators. The integrated dataset supports comparison and exploratory analysis, but causal interpretation would require additional methodology.

---

## 5. Largest Philippine Power Plants in the Dataset

The ten largest Philippine plants by installed capacity are:

| Plant | Primary Fuel | Capacity (MW) |
|---|---|---:|
| ILIJAN | Gas | 1,271.00 |
| Sual power station | Coal | 1,218.00 |
| Pagbilao power station | Coal | 1,154.00 |
| STA RITA | Gas | 1,060.00 |
| Calaca power station | Coal | 900.00 |
| KALAYAAN PSPP | Hydro | 739.20 |
| Masinloc power station | Coal | 660.00 |
| MALAYA | Oil | 650.00 |
| LIMAY CCGT | Oil | 620.00 |
| UNIFIED LEYTE | Geothermal | 610.20 |

The largest individual Philippine plant represented in the dataset is ILIJAN at 1,271 MW, followed by Sual power station at 1,218 MW and Pagbilao power station at 1,154 MW.

The largest-plant list also reflects the country's mixed installed-capacity structure, including gas, coal, hydro, oil, and geothermal facilities.

---

## 6. Philippine Share of the WRI Database Capacity

Philippine plants account for approximately:

**0.3631%**

of the total installed capacity represented by the power plants in the project's WRI-based database.

This value should be interpreted specifically as the Philippines' share of installed capacity represented in this project database.

It is not a claim that the Philippines represents 0.3631% of total real-world global electricity generation or global energy consumption.

---

## 7. Generation-Data Limitation

The PostgreSQL retrieval query for reported Philippine `generation_gwh` in 2019 returned no populated plant-level generation observations for the Philippine records under that specific field/year combination.

This must not be interpreted as zero Philippine electricity generation.

Instead, it reflects missing or unavailable generation values in the underlying WRI records used by the project.

For this reason, the project's Philippine fuel-mix analysis is based on installed capacity rather than actual electricity-generation shares.

---

## 8. Key Interpretation

The integrated 2019 dataset suggests a Philippine installed-capacity structure characterized by:

- a majority fossil-fuel capacity share of 68.53%
- coal as the largest single installed-capacity source at 42.14%
- a substantial renewable capacity share of 31.47%
- hydro and geothermal as the largest renewable capacity contributors
- a high number of solar facilities relative to their aggregate installed capacity

The findings demonstrate how the integrated pipeline can combine plant-level infrastructure with national emissions and socioeconomic indicators while preserving clear distinctions between installed capacity, generation, emissions, and economic variables.

---

## Reproducibility

The results in this document are reproducible using:

`sql/philippines_context.sql`

against the project's normalized PostgreSQL database.

The Philippine values were retrieved from the same processed data produced by the project's end-to-end transformation and loading pipeline.