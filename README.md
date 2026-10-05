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

This project develops a reproducible data engineering pipeline that integrates power plant, carbon-emissions, economic, and demographic data from multiple public sources.

The project aims to support analysis of how national power-generation profiles and installed generation capacity relate to carbon emissions, economic activity, and energy-transition patterns.

The project will eventually support country-level comparisons, clustering, and scenario-based analysis of alternative fuel-mix configurations.

---

## Data Sources

The project currently uses three approved data sources:

1. **Global Power Plant Database (WRI)**
   - Plant-level characteristics
   - Installed generation capacity
   - Primary fuel
   - Geographic information

2. **Our World in Data (OWID) CO₂ and Greenhouse Gas Emissions Dataset**
   - National emissions indicators
   - Carbon-related indicators
   - 2019 country-level snapshot used for integration

3. **World Bank Indicators REST API**
   - GDP (current US$)
   - Population, total
   - GDP per capita (current US$)
   - 2019 country-level indicators used for integration

The three sources are integrated primarily through ISO-3 country codes.

---

## Reference Integration Prototype

The validated three-source integration prototype is stored in:

```text
notebooks/01_merge_prototype.ipynb