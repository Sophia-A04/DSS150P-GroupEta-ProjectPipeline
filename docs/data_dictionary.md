\# Data Dictionary — Curated Integrated Dataset



\*\*Project:\*\* DSS150P Group Eta — Data Engineering Pipeline

\*\*Dataset:\*\* `eta\_curated\_2019.parquet`

\*\*Location:\*\* `data/curated/eta\_curated\_2019.parquet`

\*\*Producer:\*\* `src/transform/run\_curated.py` → `integrate\_sources.build\_curated\_dataset()`

\*\*Validation:\*\* `python -m src.validate.integration\_validation` → 24 checks, 0 errors, 1 warning

\*\*Consumers:\*\* PostgreSQL loader (`src/load/`), analytics layer, presentation / technical defense



\## Grain



One row = one real power plant. Row count is 34,936 and matches the WRI raw plant count

exactly. The primary key is `gppd\_idnr` (unique = 34,936).



Country-level indicators (OWID CO₂, World Bank GDP/population) are attached by a many-to-one

left join on ISO-3 country code. Unmatched countries are retained; their country-level fields

are null rather than dropped, so the plant-level grain is never broken.



\## Schema (162 columns)



Every value in the \*\*Type\*\*, \*\*Nulls\*\*, \*\*Unique\*\*, and \*\*Example\*\* columns below is taken

from the live profile of `eta\_curated\_2019.parquet`.



\### A. Plant identity and location (from WRI)



| Field | Type | Nulls | Unique | Description | Example |

|-------|------|-------|--------|-------------|---------|

| `gppd\_idnr` | string | 0 | 34,936 | WRI/GPPD plant identifier; primary key | `GEODB0040538` |

| `name` | string | 0 | 34,528 | Plant name as reported by WRI | `Kajaki Hydroelectric Power Plant Afghanistan` |

| `country` | string | 0 | 167 | ISO-3 country code of the plant; join key to OWID and World Bank | `AFG` |

| `country\_long` | string | 0 | 167 | Full country name | `Afghanistan` |

| `latitude` | float64 | 0 | 31,779 | Plant latitude, WGS-84 | `32.322` |

| `longitude` | float64 | 0 | 33,036 | Plant longitude, WGS-84 | `65.119` |



\### B. Capacity and fuel (from WRI)



| Field | Type | Nulls | Description | Example |

|-------|------|-------|-------------|---------|

| `capacity\_mw` | float64 | 0 | Installed capacity in MW | `33.0` |

| `primary\_fuel` | string | 0 | Primary fuel category (15 distinct values) | `Hydro` |

| `other\_fuel1` | string | 32,992 | Secondary fuel if any | `Oil` |

| `other\_fuel2` | string | 34,660 | Tertiary fuel if any | `Other` |

| `other\_fuel3` | string | 34,844 | Quaternary fuel if any | `Other` |

| `commissioning\_year` | float64 | 17,489 | Year plant began operating | `1965.0` |

| `owner` | string | 14,068 | Owner name; source-faithful, some entries carry CSV encoding artifacts | `SociÃ©te AlgÃ©rienne de Production de l'Electricité` |

| `source` | string | 15 | WRI source attribution for the plant record | `GEODB` |

| `url` | string | 18 | Source URL for the plant record | `http://globalenergyobservatory.org` |

| `geolocation\_source` | string | 419 | Source of the coordinates | `GEODB` |

| `wepp\_id` | string | 18,702 | WEPP database identifier | `1009793` |

| `year\_of\_capacity\_data` | float64 | 20,049 | Year the capacity figure refers to | `2017.0` |



\### C. Historical generation (from WRI, 2013–2019)



| Field | Type | Nulls | Example |

|-------|------|-------|---------|

| `generation\_gwh\_2013` | float64 | 28,519 | `89.59527777777778` |

| `generation\_gwh\_2014` | float64 | 27,710 | `102.64277777777778` |

| `generation\_gwh\_2015` | float64 | 26,733 | `96.55555555555556` |

| `generation\_gwh\_2016` | float64 | 25,792 | `95.87277777777778` |

| `generation\_gwh\_2017` | float64 | 25,436 | `85.90027777777777` |

| `generation\_gwh\_2018` | float64 | 25,299 | `92.68222222222222` |

| `generation\_gwh\_2019` | float64 | 25,277 | `2.467` |

| `generation\_data\_source` | string | 23,536 | `Australia Clean Energy Regulator` |

| `estimated\_generation\_gwh\_2013` | float64 | 18,816 | `123.77` |

| `estimated\_generation\_gwh\_2014` | float64 | 18,433 | `162.9` |

| `estimated\_generation\_gwh\_2015` | float64 | 17,886 | `97.39` |

| `estimated\_generation\_gwh\_2016` | float64 | 17,366 | `137.76` |

| `estimated\_generation\_gwh\_2017` | float64 | 1,798 | `119.5` |

| `estimated\_generation\_note\_2013` | string | 0 | `HYDRO-V1` |

| `estimated\_generation\_note\_2014` | string | 0 | `HYDRO-V1` |

| `estimated\_generation\_note\_2015` | string | 0 | `HYDRO-V1` |

| `estimated\_generation\_note\_2016` | string | 0 | `HYDRO-V1` |

| `estimated\_generation\_note\_2017` | string | 0 | `HYDRO-V1` |



`generation\_gwh\_2019` may contain negative values. This is a source-side issue and is

classified as a warning by raw WRI validation, not an error. See `docs/known\_issues.md`.



\### D. Derived capacity features



Produced by `src/transform/capacity\_features.py`.



| Field | Type | Nulls | Description | Example |

|-------|------|-------|-------------|---------|

| `total\_plant\_count` | int64 | 0 | Plants in the same country / primary-fuel group | `9` |

| `total\_installed\_capacity\_mw` | float64 | 0 | Total installed capacity for the plant's country | `300.55` |

| `Biomass\_capacity\_mw` | float64 | 0 | Biomass capacity in the country, MW | `0.0` |

| `Coal\_capacity\_mw` | float64 | 0 | Coal capacity in the country, MW | `0.0` |

| `Cogeneration\_capacity\_mw` | float64 | 0 | Cogeneration capacity in the country, MW | `0.0` |

| `Gas\_capacity\_mw` | float64 | 0 | Gas capacity in the country, MW | `42.0` |

| `Geothermal\_capacity\_mw` | float64 | 0 | Geothermal capacity in the country, MW | `0.0` |

| `Hydro\_capacity\_mw` | float64 | 0 | Hydro capacity in the country, MW | `238.55` |

| `Nuclear\_capacity\_mw` | float64 | 0 | Nuclear capacity in the country, MW | `0.0` |

| `Oil\_capacity\_mw` | float64 | 0 | Oil capacity in the country, MW | `0.0` |

| `Other\_capacity\_mw` | float64 | 0 | Other capacity in the country, MW | `0.0` |

| `Petcoke\_capacity\_mw` | float64 | 0 | Petcoke capacity in the country, MW | `0.0` |

| `Solar\_capacity\_mw` | float64 | 0 | Solar capacity in the country, MW | `20.0` |

| `Storage\_capacity\_mw` | float64 | 0 | Storage capacity in the country, MW | `0.0` |

| `Waste\_capacity\_mw` | float64 | 0 | Waste capacity in the country, MW | `0.0` |

| `Wave and Tidal\_capacity\_mw` | float64 | 0 | Wave and tidal capacity in the country, MW | `0.0` |

| `Wind\_capacity\_mw` | float64 | 0 | Wind capacity in the country, MW | `0.0` |

| `Biomass\_share\_pct` | float64 | 0 | Biomass share of the country total, percent | `0.0` |

| `Coal\_share\_pct` | float64 | 0 | Coal share of the country total, percent | `0.0` |

| `Cogeneration\_share\_pct` | float64 | 0 | Cogeneration share of the country total, percent | `0.0` |

| `Gas\_share\_pct` | float64 | 0 | Gas share of the country total, percent | `13.974380302778238` |

| `Geothermal\_share\_pct` | float64 | 0 | Geothermal share of the country total, percent | `0.0` |

| `Hydro\_share\_pct` | float64 | 0 | Hydro share of the country total, percent | `79.37115288637499` |

| `Nuclear\_share\_pct` | float64 | 0 | Nuclear share of the country total, percent | `0.0` |

| `Oil\_share\_pct` | float64 | 0 | Oil share of the country total, percent | `0.0` |

| `Other\_share\_pct` | float64 | 0 | Other share of the country total, percent | `0.0` |

| `Petcoke\_share\_pct` | float64 | 0 | Petcoke share of the country total, percent | `0.0` |

| `Solar\_share\_pct` | float64 | 0 | Solar share of the country total, percent | `6.65446681084678` |

| `Storage\_share\_pct` | float64 | 0 | Storage share of the country total, percent | `0.0` |

| `Waste\_share\_pct` | float64 | 0 | Waste share of the country total, percent | `0.0` |

| `Wave and Tidal\_share\_pct` | float64 | 0 | Wave and tidal share of the country total, percent | `0.0` |

| `Wind\_share\_pct` | float64 | 0 | Wind share of the country total, percent | `0.0` |

| `fossil\_capacity\_mw` | float64 | 0 | Fossil-fuel group capacity in the country, MW | `42.0` |

| `renewable\_capacity\_mw` | float64 | 0 | Renewable group capacity in the country, MW | `258.55` |

| `other\_or\_unclassified\_capacity\_mw` | float64 | 0 | Other / unclassified group capacity in the country, MW | `0.0` |

| `fossil\_share\_pct` | float64 | 0 | Fossil group share of the country total, percent | `13.974380302778238` |

| `renewable\_share\_pct` | float64 | 0 | Renewable group share of the country total, percent | `86.02561969722176` |

| `other\_or\_unclassified\_share\_pct` | float64 | 0 | Other / unclassified group share of the country total, percent | `0.0` |

| `country\_primary\_fuel\_plant\_count` | int64 | 0 | Plants of the same primary fuel in the country | `6` |

| `country\_primary\_fuel\_capacity\_mw` | float64 | 0 | Capacity of the same primary fuel in the country, MW | `238.55` |

| `country\_primary\_fuel\_capacity\_share\_pct` | float64 | 0 | Share of the same primary fuel within the country, percent | `79.37115288637499` |



\### E. OWID 2019 country indicators



Joined on `country` = `iso\_code`.



| Field | Type | Nulls | Description | Example |

|-------|------|-------|-------------|---------|

| `owid\_country` | string | 9 | OWID country name | `Afghanistan` |

| `year` | float64 | 9 | Always 2019 | `2019.0` |

| `iso\_code` | string | 9 | ISO-3 code | `AFG` |

| `co2` | float64 | 9 | Total CO₂, million tonnes | `10.400110244750977` |

| `co2\_per\_capita` | float64 | 11 | Tonnes CO₂ per person | `0.2747272849082947` |

| `co2\_growth\_abs` | float64 | 9 | Year-over-year CO₂ change, million tonnes | `0.2086060047149658` |

| `co2\_growth\_prct` | float64 | 11 | Year-over-year CO₂ change, percent | `2.0468592643737797` |

| `coal\_co2` | float64 | 291 | CO₂ from coal, million tonnes | `3.273106098175049` |

| `gas\_co2` | float64 | 546 | CO₂ from gas, million tonnes | `0.2455749958753585` |

| `oil\_co2` | float64 | 11 | CO₂ from oil, million tonnes | `6.8431010246276855` |

| `methane` | float64 | 12 | Methane emissions, million tonnes CO₂-equivalent | `15.215601921081545` |

| `nitrous\_oxide` | float64 | 12 | Nitrous oxide emissions, million tonnes CO₂-equivalent | `4.597519397735596` |

| `total\_ghg` | float64 | 12 | Total greenhouse gases, million tonnes CO₂-equivalent | `36.55088806152344` |

| `primary\_energy\_consumption` | float64 | 9 | Total primary energy, TWh | `47.11153030395508` |

| `share\_global\_co2` | float64 | 9 | Country share of global CO₂, percent | `0.0280427951365709` |

| `owid\_2019\_matched` | bool | 0 | True when the plant's country matched OWID 2019 | `True` |



Additional OWID columns are carried through the many-to-one join unchanged. They include

`cement\_co2`, `cement\_co2\_per\_capita`, `co2\_including\_luc`, `co2\_including\_luc\_growth\_abs`,

`co2\_including\_luc\_growth\_prct`, `co2\_including\_luc\_per\_capita`, `co2\_including\_luc\_per\_gdp`,

`co2\_including\_luc\_per\_unit\_energy`, `co2\_per\_gdp`, `co2\_per\_unit\_energy`,

`coal\_co2\_per\_capita`, `consumption\_co2`, `consumption\_co2\_per\_capita`,

`consumption\_co2\_per\_gdp`, `cumulative\_cement\_co2`, `cumulative\_co2`,

`cumulative\_co2\_including\_luc`, `cumulative\_coal\_co2`, `cumulative\_flaring\_co2`,

`cumulative\_gas\_co2`, `cumulative\_luc\_co2`, `cumulative\_oil\_co2`, `cumulative\_other\_co2`,

`energy\_per\_capita`, `energy\_per\_gdp`, `flaring\_co2`, `flaring\_co2\_per\_capita`,

`gas\_co2\_per\_capita`, `ghg\_excluding\_lucf\_per\_capita`, `ghg\_per\_capita`,

`land\_use\_change\_co2`, `land\_use\_change\_co2\_per\_capita`, `methane\_per\_capita`,

`nitrous\_oxide\_per\_capita`, `oil\_co2\_per\_capita`, `other\_co2\_per\_capita`,

`other\_industry\_co2`, `share\_global\_cement\_co2`, `share\_global\_co2\_including\_luc`,

`share\_global\_coal\_co2`, `share\_global\_cumulative\_cement\_co2`,

`share\_global\_cumulative\_co2`, `share\_global\_cumulative\_co2\_including\_luc`,

`share\_global\_cumulative\_coal\_co2`, `share\_global\_cumulative\_flaring\_co2`,

`share\_global\_cumulative\_gas\_co2`, `share\_global\_cumulative\_luc\_co2`,

`share\_global\_cumulative\_oil\_co2`, `share\_global\_cumulative\_other\_co2`,

`share\_global\_flaring\_co2`, `share\_global\_gas\_co2`, `share\_global\_luc\_co2`,

`share\_global\_oil\_co2`, `share\_global\_other\_co2`, `share\_of\_temperature\_change\_from\_ghg`,

`temperature\_change\_from\_ch4`, `temperature\_change\_from\_co2`,

`temperature\_change\_from\_ghg`, `temperature\_change\_from\_n2o`,

`total\_ghg\_excluding\_lucf`, `trade\_co2`, `trade\_co2\_share`.



\### F. World Bank 2019 country indicators



Joined on `country` = `wb\_iso\_code`.



| Field | Type | Nulls | Description | Example |

|-------|------|-------|-------------|---------|

| `wb\_iso\_code` | string | 50 | ISO-3 code | `AFG` |

| `wb\_country` | string | 50 | World Bank country name | `Afghanistan` |

| `wb\_year` | float64 | 50 | Always 2019 | `2019.0` |

| `wb\_gdp\_current\_usd` | float64 | 90 | GDP, current US$ | `18799444490.1128` |

| `wb\_population` | float64 | 50 | Total population | `37856121.0` |

| `wb\_gdp\_per\_capita\_current\_usd` | float64 | 90 | GDP per capita, current US$ | `496.6025042585` |

| `wb\_2019\_matched` | bool | 0 | True when the plant's country matched World Bank 2019 | `True` |



`wb\_gdp\_current\_usd` and `wb\_gdp\_per\_capita\_current\_usd` have more nulls than the

match flag. The integrated validator flags 40 rows as WB-matched but with null GDP.

See `docs/known\_issues.md`.



\## Nullability Summary



| Class | Rule | Example fields |

|-------|------|----------------|

| Required | Identity, capacity, plant fuel, and match flags | `gppd\_idnr`, `country`, `name`, `capacity\_mw`, `primary\_fuel`, `owid\_2019\_matched`, `wb\_2019\_matched` |

| Optional | Country-level indicators when the plant's country has no match in that source | all OWID and WB value columns |

| Source-faithful | WRI history columns for plants without that year's data | `generation\_gwh\_2013` through `generation\_gwh\_2019` |



\## Units and Conventions



Capacity is in MW. Generation is in GWh. GHG indicators are in million tonnes of

CO₂-equivalent, following OWID convention. GDP is in current US$. Population is in

persons. ISO-3 country codes are uppercase and three letters. Share columns are in

percent and lie between 0 and 100.



\## Provenance



| Source | Type | Role | Retrieval |

|--------|------|------|-----------|

| WRI Global Power Plant Database | CSV | Plant-level base | Raw file, retained as CSV |

| Our World in Data CO₂ dataset | CSV | Country CO₂ and GHG | Raw file, retained as CSV |

| World Bank Indicators API | JSON via REST | Country GDP and population | Programmatic, 2019 slice |

