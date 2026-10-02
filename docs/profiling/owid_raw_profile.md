# Raw Profile: owid_raw

- Source file: `data\raw\owid-co2-data-1.csv`
- Profiled at (UTC): 2026-10-02T04:22:53+00:00
- Rows: 50,411
- Columns: 79
- Fully duplicated rows: 0
- Memory (MB): 34.81

| column | dtype | nulls | null % | unique | min | max |
|---|---|---|---|---|---|---|
| country | str | 0 | 0.0 | 254 |  |  |
| year | int64 | 0 | 0.0 | 275 | 1750.0 | 2024.0 |
| iso_code | str | 7931 | 15.73 | 218 |  |  |
| population | float64 | 9244 | 18.34 | 40197 | 215.0 | 8161972574.0 |
| gdp | float64 | 35160 | 69.75 | 15249 | 49980000.0 | 130112562171125.0 |
| cement_co2 | float64 | 21238 | 42.13 | 5482 | 0.0 | 1666.885 |
| cement_co2_per_capita | float64 | 24763 | 49.12 | 730 | 0.0 | 2.484 |
| co2 | float64 | 21027 | 41.71 | 16509 | 0.0 | 38598.578 |
| co2_growth_abs | float64 | 23195 | 46.01 | 9483 | -1928.339 | 1804.657 |
| co2_growth_prct | float64 | 24172 | 47.95 | 16636 | -100.0 | 180870.0 |
| co2_including_luc | float64 | 26615 | 52.8 | 20388 | -84.56 | 43184.086 |
| co2_including_luc_growth_abs | float64 | 26915 | 53.39 | 12982 | -2298.978 | 2614.874 |
| co2_including_luc_growth_prct | float64 | 26915 | 53.39 | 17054 | -11927.241 | 6362.499 |
| co2_including_luc_per_capita | float64 | 26654 | 52.87 | 12700 | -12.455 | 364.809 |
| co2_including_luc_per_gdp | float64 | 33621 | 66.69 | 5454 | -12.938 | 291.293 |
| co2_including_luc_per_unit_energy | float64 | 40278 | 79.9 | 10032 | -8673.521 | 511469.312 |
| co2_per_capita | float64 | 23902 | 47.41 | 8873 | 0.0 | 782.743 |
| co2_per_gdp | float64 | 32883 | 65.23 | 1721 | 0.0 | 82.599 |
| co2_per_unit_energy | float64 | 39585 | 78.52 | 10438 | 0.0 | 10688.897 |
| coal_co2 | float64 | 28486 | 56.51 | 10912 | 0.0 | 15805.254 |
| coal_co2_per_capita | float64 | 29097 | 57.72 | 4998 | 0.0 | 34.295 |
| consumption_co2 | float64 | 45358 | 89.98 | 4929 | 0.0 | 38598.578 |
| consumption_co2_per_capita | float64 | 45768 | 90.79 | 3811 | 0.0 | 63.272 |
| consumption_co2_per_gdp | float64 | 45963 | 91.18 | 847 | 0.0 | 3.306 |
| cumulative_cement_co2 | float64 | 21260 | 42.17 | 10545 | 0.0 | 49693.922 |
| cumulative_co2 | float64 | 22848 | 45.32 | 21820 | 0.0 | 1849123.875 |
| cumulative_co2_including_luc | float64 | 26615 | 52.8 | 23373 | -120.345 | 2751504.25 |
| cumulative_coal_co2 | float64 | 28486 | 56.51 | 16489 | 0.0 | 849832.25 |
| cumulative_flaring_co2 | float64 | 34300 | 68.04 | 5234 | 0.0 | 20141.375 |
| cumulative_gas_co2 | float64 | 32264 | 64.0 | 8328 | 0.0 | 276572.688 |
| cumulative_luc_co2 | float64 | 12961 | 25.71 | 33272 | -3918.006 | 906953.562 |
| cumulative_oil_co2 | float64 | 24953 | 49.5 | 17949 | 0.0 | 638014.188 |
| cumulative_other_co2 | float64 | 47157 | 93.55 | 2136 | 0.0 | 14869.403 |
| energy_per_capita | float64 | 39825 | 79.0 | 10498 | 0.0 | 318559.688 |
| energy_per_gdp | float64 | 42624 | 84.55 | 3221 | 0.0 | 25.253 |
| flaring_co2 | float64 | 34237 | 67.92 | 3697 | 0.0 | 432.392 |
| flaring_co2_per_capita | float64 | 35501 | 70.42 | 1035 | 0.0 | 114.509 |
| gas_co2 | float64 | 32264 | 64.0 | 6531 | 0.0 | 8009.828 |
| gas_co2_per_capita | float64 | 32965 | 65.39 | 3146 | 0.0 | 53.476 |
| ghg_excluding_lucf_per_capita | float64 | 14569 | 28.9 | 9220 | 0.022 | 369.65 |
| ghg_per_capita | float64 | 14232 | 28.23 | 16049 | -28.852 | 369.705 |
| land_use_change_co2 | float64 | 12961 | 25.71 | 22250 | -319.418 | 8692.767 |
| land_use_change_co2_per_capita | float64 | 13776 | 27.33 | 13101 | -45.317 | 305.195 |
| methane | float64 | 12261 | 24.32 | 19110 | 0.0 | 9498.914 |
| methane_per_capita | float64 | 14232 | 28.23 | 5657 | 0.032 | 133.104 |
| nitrous_oxide | float64 | 11911 | 23.63 | 12888 | 0.0 | 2935.779 |
| nitrous_oxide_per_capita | float64 | 13972 | 27.72 | 2784 | 0.0 | 20.393 |
| oil_co2 | float64 | 24952 | 49.5 | 11073 | 0.0 | 12470.596 |
| oil_co2_per_capita | float64 | 25689 | 50.96 | 6001 | 0.0 | 782.743 |
| other_co2_per_capita | float64 | 47752 | 94.73 | 317 | 0.0 | 0.604 |
| other_industry_co2 | float64 | 47157 | 93.55 | 1748 | 0.0 | 458.178 |
| primary_energy_consumption | float64 | 39780 | 78.91 | 9695 | 0.0 | 176737.094 |
| share_global_cement_co2 | float64 | 28141 | 55.82 | 3659 | 0.0 | 100.0 |
| share_global_co2 | float64 | 22848 | 45.32 | 4964 | 0.0 | 100.0 |
| share_global_co2_including_luc | float64 | 26615 | 52.8 | 5431 | -0.375 | 100.0 |
| share_global_coal_co2 | float64 | 28486 | 56.51 | 4880 | 0.0 | 100.0 |
| share_global_cumulative_cement_co2 | float64 | 28141 | 55.82 | 3529 | 0.0 | 100.0 |
| share_global_cumulative_co2 | float64 | 22848 | 45.32 | 4593 | 0.0 | 100.0 |
| share_global_cumulative_co2_including_luc | float64 | 26615 | 52.8 | 5014 | -0.101 | 100.0 |
| share_global_cumulative_coal_co2 | float64 | 28486 | 56.51 | 4503 | 0.0 | 100.0 |
| share_global_cumulative_flaring_co2 | float64 | 39322 | 78.0 | 2691 | 0.0 | 100.0 |
| share_global_cumulative_gas_co2 | float64 | 35244 | 69.91 | 2774 | 0.0 | 100.0 |
| share_global_cumulative_luc_co2 | float64 | 12961 | 25.71 | 5889 | -0.518 | 100.0 |
| share_global_cumulative_oil_co2 | float64 | 26578 | 52.72 | 4538 | 0.0 | 100.0 |
| share_global_cumulative_other_co2 | float64 | 48241 | 95.7 | 1172 | 0.0 | 100.0 |
| share_global_flaring_co2 | float64 | 39322 | 78.0 | 2900 | 0.0 | 100.0 |
| share_global_gas_co2 | float64 | 35244 | 69.91 | 3121 | 0.0 | 100.0 |
| share_global_luc_co2 | float64 | 12961 | 25.71 | 6436 | -6.966 | 100.0 |
| share_global_oil_co2 | float64 | 26578 | 52.72 | 4662 | 0.0 | 100.0 |
| share_global_other_co2 | float64 | 48241 | 95.7 | 1267 | 0.0 | 100.0 |
| share_of_temperature_change_from_ghg | float64 | 9173 | 18.2 | 6040 | -0.824 | 100.0 |
| temperature_change_from_ch4 | float64 | 12131 | 24.06 | 210 | -0.001 | 0.377 |
| temperature_change_from_co2 | float64 | 9173 | 18.2 | 451 | 0.0 | 1.216 |
| temperature_change_from_ghg | float64 | 9173 | 18.2 | 548 | -0.001 | 1.678 |
| temperature_change_from_n2o | float64 | 12131 | 24.06 | 81 | 0.0 | 0.085 |
| total_ghg | float64 | 12261 | 24.32 | 26443 | -19.725 | 54433.398 |
| total_ghg_excluding_lucf | float64 | 12598 | 24.99 | 18567 | 0.0 | 43714.777 |
| trade_co2 | float64 | 45699 | 90.65 | 4328 | -2177.807 | 1768.846 |
| trade_co2_share | float64 | 45699 | 90.65 | 4453 | -98.281 | 1023.042 |
