# Raw Profile: wri_raw

- Source file: `data\raw\wri\global_power_plant_database.csv`
- Profiled at (UTC): 2026-10-05T02:29:33+00:00
- Rows: 34,936
- Columns: 36
- Fully duplicated rows: 0
- Memory (MB): 41.59

| column | dtype | nulls | null % | unique | min | max |
|---|---|---|---|---|---|---|
| country | str | 0 | 0.0 | 167 |  |  |
| country_long | str | 0 | 0.0 | 167 |  |  |
| name | str | 0 | 0.0 | 34528 |  |  |
| gppd_idnr | str | 0 | 0.0 | 34936 |  |  |
| capacity_mw | float64 | 0 | 0.0 | 5611 | 1.0 | 22500.0 |
| latitude | float64 | 0 | 0.0 | 31779 | -77.847 | 71.292 |
| longitude | float64 | 0 | 0.0 | 33036 | -179.9777 | 179.3887 |
| primary_fuel | str | 0 | 0.0 | 15 |  |  |
| other_fuel1 | str | 32992 | 94.44 | 12 |  |  |
| other_fuel2 | str | 34660 | 99.21 | 11 |  |  |
| other_fuel3 | str | 34844 | 99.74 | 8 |  |  |
| commissioning_year | float64 | 17489 | 50.06 | 2023 | 1896.0 | 2020.0 |
| owner | str | 14068 | 40.27 | 10144 |  |  |
| source | str | 15 | 0.04 | 866 |  |  |
| url | str | 18 | 0.05 | 4870 |  |  |
| geolocation_source | str | 419 | 1.2 | 28 |  |  |
| wepp_id | str | 18702 | 53.53 | 15263 |  |  |
| year_of_capacity_data | float64 | 20049 | 57.39 | 11 | 2000.0 | 2019.0 |
| generation_gwh_2013 | float64 | 28519 | 81.63 | 5458 | -947.6 | 50834.0 |
| generation_gwh_2014 | float64 | 27710 | 79.32 | 6159 | -989.619 | 32320.917 |
| generation_gwh_2015 | float64 | 26733 | 76.52 | 7037 | -864.428 | 37433.607 |
| generation_gwh_2016 | float64 | 25792 | 73.83 | 7671 | -768.62 | 32377.477 |
| generation_gwh_2017 | float64 | 25436 | 72.81 | 7974 | -934.944 | 36448.643 |
| generation_gwh_2018 | float64 | 25299 | 72.42 | 7946 | -982.622 | 35136.0 |
| generation_gwh_2019 | float64 | 25277 | 72.35 | 8327 | -780.339 | 31920.368 |
| generation_data_source | str | 23536 | 67.37 | 17 |  |  |
| estimated_generation_gwh_2013 | float64 | 18816 | 53.86 | 8845 | 1.12 | 48675.06 |
| estimated_generation_gwh_2014 | float64 | 18433 | 52.76 | 9027 | 0.87 | 58470.77 |
| estimated_generation_gwh_2015 | float64 | 17886 | 51.2 | 9113 | 0.44 | 57113.35 |
| estimated_generation_gwh_2016 | float64 | 17366 | 49.71 | 9280 | 0.3 | 60859.73 |
| estimated_generation_gwh_2017 | float64 | 1798 | 5.15 | 15023 | 0.0 | 82810.77 |
| estimated_generation_note_2013 | str | 0 | 0.0 | 5 |  |  |
| estimated_generation_note_2014 | str | 0 | 0.0 | 5 |  |  |
| estimated_generation_note_2015 | str | 0 | 0.0 | 5 |  |  |
| estimated_generation_note_2016 | str | 0 | 0.0 | 5 |  |  |
| estimated_generation_note_2017 | str | 0 | 0.0 | 6 |  |  |
