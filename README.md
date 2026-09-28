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

This project develops a data engineering pipeline for integrating global power plant data with national carbon emissions and economic indicators.

The project aims to support analysis of how national power-generation profiles and installed capacity relate to carbon emissions, economic activity, and energy-transition patterns.

The project will eventually support country-level comparisons, clustering, and scenario-based analysis of alternative fuel-mix configurations.

---

## Data Sources

The project currently uses data from:

1. Global Power Plant Database
2. Our World in Data — CO2 and Greenhouse Gas Emissions

These datasets are integrated using country-level identifiers and related attributes.

---

## Current Prototype Status

A validated merge prototype has been completed and is stored in:

```text
notebooks/01_merge_prototype.ipynb