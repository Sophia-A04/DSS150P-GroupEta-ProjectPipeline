# Three-Source Integration Rules and Assumptions

## Purpose

This document records the integration rules and assumptions used by Group Eta's validated three-source reference prototype.

The reference implementation is located at `notebooks/01_merge_prototype.ipynb`.

The integrated dataset combines:

1. WRI Global Power Plant Database
2. Our World in Data (OWID) CO₂ and Greenhouse Gas Emissions Dataset
3. World Bank Indicators API

The prototype serves as the baseline for the later production transformation pipeline.

---

## 1. Analytical Grain

The Global Power Plant Database is the base dataset.

The natural grain of the integrated dataset is:

**ONE ROW = ONE REAL POWER PLANT**

Each `gppd_idnr` should therefore represent one unique plant record.

Country-level datasets and calculated country-level features must not change this grain.

The validated reference output contains approximately:

- 34,936 plant rows
- 34,936 unique `gppd_idnr` values
- 167 countries
- 123 Philippine plant rows

The integration must not introduce artificial row duplication or row inflation.

---

## 2. Source Roles

### WRI Global Power Plant Database

WRI provides the plant-level foundation of the dataset.

Examples of plant-level information include:

- Plant identifier
- Plant name
- Country
- Installed capacity
- Primary fuel
- Latitude
- Longitude
- Other plant attributes available in the source

The WRI plant table remains the left/base table during final integration.

### Our World in Data

OWID provides national emissions and carbon-related indicators.

The integration uses a 2019 country-level snapshot.

OWID is treated as the project's source for emissions-related indicators.

GDP and population fields available in OWID are not used as the primary economic or demographic variables in the final integration because those concepts are assigned to the World Bank source.

### World Bank

World Bank Indicators provide national economic and demographic indicators for 2019.

The reference prototype uses:

- GDP (current US$)
- Population, total
- GDP per capita (current US$)

World Bank is treated as the project's source for these economic and demographic variables.

---

## 3. Integration Year

The common analytical snapshot year is **2019**.

OWID and World Bank country-level indicators are aligned to 2019 before enrichment of plant-level records.

Plant records themselves remain individual real power plants rather than being aggregated into country-level observations.

---

## 4. Country Identifier

ISO-3 country codes are the primary country-level integration key.

Conceptually:

WRI `country` ↔ OWID `iso_code` ↔ World Bank ISO-3 country code

Country names may be retained for readability and verification, but country names are not the primary merge key.

---

## 5. Join Relationships

The expected relationships are:

- Many WRI plant records may belong to one OWID country record.
- Many WRI plant records may belong to one World Bank country record.

Country-level enrichment tables must therefore contain no more than one applicable row per ISO-3 country code for the 2019 snapshot before being merged with plant records.

Many-to-one merge validation should be used where appropriate in the production implementation.

---

## 6. Join Type

Plant records are preserved using left joins when country-level datasets are attached to the WRI plant table.

Conceptually:

WRI plants → LEFT JOIN OWID → LEFT JOIN World Bank

A legitimate power plant should not be removed simply because an OWID or World Bank record is unavailable for its country.

Unmatched country-level indicators should remain missing.

Missing values must not automatically be interpreted or replaced as zero.

---

## 7. Match Indicators

The reference integration maintains source-match indicators such as:

- `owid_2019_matched`
- `wb_2019_matched`

These fields identify whether an individual plant's ISO-3 country code successfully matched the corresponding country-level source.

They should remain logically consistent with the actual source joins.

---

## 8. Country-Level Installed-Capacity Features

Country-level installed-capacity statistics are derived from the WRI plant records.

Examples include:

- `total_installed_capacity_mw`
- `country_primary_fuel_capacity_mw`
- `country_primary_fuel_capacity_share_pct`
- `fossil_share_pct`
- `renewable_share_pct`

These statistics are calculated at country or country-fuel level temporarily.

They are then joined back to the individual plant rows.

The final dataset must not be reduced to one row per country.

---

## 9. Installed Capacity vs. Electricity Generation

Installed generation capacity and actual electricity generation are different concepts.

`capacity_mw` represents installed generation capacity.

`generation_gwh` represents actual electricity generation where available.

Therefore:

- Installed-capacity shares must not be described as electricity-generation shares.
- Missing generation values must not be interpreted as zero generation.
- Generation data are not required to preserve the plant-level analytical grain.

---

## 10. Missing Values

Missing values from legitimate source records are preserved unless a documented transformation rule specifically requires otherwise.

The integration does not fabricate unavailable OWID or World Bank values.

Country-level records that fail to match a legitimate WRI plant remain represented by the plant record with missing enrichment fields.

---

## 11. World Bank Aggregate Records

World Bank responses may contain entities that are not individual countries, such as regional or aggregate records.

Only appropriate country-level observations with usable country identifiers should participate in the plant-level country integration.

Aggregate World Bank entities must not create artificial plant matches.

---

## 12. Philippines Preservation

The Philippines must remain present throughout integration.

The validated prototype contains approximately **123 Philippine plant rows**.

Philippine plant records are expected to retain:

- WRI plant-level information
- OWID 2019 emissions indicators
- World Bank 2019 economic and demographic indicators
- Installed-capacity features

The prototype's Philippines checks are primarily integration-integrity checks.

The project's final Philippines-focused analytical interpretation will be performed during a later project stage.

---

## 13. Reference Regression Characteristics

The validated three-source prototype currently produces approximately:

- Rows: 34,936
- Unique plant IDs: 34,936
- Countries: 167
- Philippine plant rows: 123
- OWID-matched plant rows: 34,927
- World Bank-matched plant rows: 34,886

These values serve as regression references for later production transformation development.

They should not be treated as arbitrary hard-coded replacement values.

The production transformation pipeline should reproduce the reference behavior from the source data rather than manually constructing these counts.

---

## 14. Reproducibility Principle

The notebook is the validated reference implementation, but it is not intended to remain the final production transformation mechanism.

The production pipeline should eventually reproduce the same integration logic through reusable modules following:

**RAW → STAGING → CURATED**

The manually generated reference CSV may be used for comparison and regression checking, but the production pipeline must not depend on that CSV as its transformation input.

---

## 15. Validation Expectations

Later production implementations should preserve the following principles:

- One unique plant identifier per plant row
- No artificial row inflation
- Valid ISO-3 country identifiers
- One country-level OWID record per integration key
- One country-level World Bank record per integration key
- Plant-level row count preserved through country-level enrichment
- Philippines retained
- Installed-capacity shares remain within valid percentage ranges
- Source-match flags remain consistent with source availability
- Missing enrichment values are not fabricated

Existing validation modules under `src/validate/` should be reused rather than creating a separate competing validation framework.