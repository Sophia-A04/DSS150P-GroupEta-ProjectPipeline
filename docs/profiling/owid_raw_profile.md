# Raw Profile: owid_raw

- Source file: `data\raw\owid\owid-co2-data.csv`
- Profiled at (UTC): 2026-10-05T02:29:34+00:00
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
| cement_co2 | float64 | 21238 | 42.13 | 10944 | 0.0 | 1666.885 |
| cement_co2_per_capita | float64 | 24763 | 49.12 | 13185 | 0.0 | 2.4839 |
| co2 | float64 | 21027 | 41.71 | 22060 | 0.0 | 38598.5781 |
| co2_growth_abs | float64 | 23195 | 46.01 | 19649 | -1928.3395 | 1804.6566 |
| co2_growth_prct | float64 | 24172 | 47.95 | 22533 | -100.0 | 180870.0 |
| co2_including_luc | float64 | 26615 | 52.8 | 23320 | -84.5602 | 43184.0859 |
| co2_including_luc_growth_abs | float64 | 26915 | 53.39 | 22906 | -2298.9783 | 2614.874 |
| co2_including_luc_growth_prct | float64 | 26915 | 53.39 | 23069 | -11927.2412 | 6362.4985 |
| co2_including_luc_per_capita | float64 | 26654 | 52.87 | 23746 | -12.4546 | 364.8094 |
| co2_including_luc_per_gdp | float64 | 33621 | 66.69 | 16771 | -12.9381 | 291.293 |
| co2_including_luc_per_unit_energy | float64 | 40278 | 79.9 | 10101 | -8673.5205 | 511469.3125 |
| co2_per_capita | float64 | 23902 | 47.41 | 26024 | 0.0 | 782.7434 |
| co2_per_gdp | float64 | 32883 | 65.23 | 17318 | 0.0 | 82.5989 |
| co2_per_unit_energy | float64 | 39585 | 78.52 | 10698 | 0.0 | 10688.8975 |
| coal_co2 | float64 | 28486 | 56.51 | 15356 | 0.0 | 15805.2539 |
| coal_co2_per_capita | float64 | 29097 | 57.72 | 19619 | 0.0 | 34.2951 |
| consumption_co2 | float64 | 45358 | 89.98 | 5019 | 0.0 | 38598.5781 |
| consumption_co2_per_capita | float64 | 45768 | 90.79 | 4642 | 0.0 | 63.2716 |
| consumption_co2_per_gdp | float64 | 45963 | 91.18 | 4447 | 0.0 | 3.3057 |
| cumulative_cement_co2 | float64 | 21260 | 42.17 | 12741 | 0.0 | 49693.9219 |
| cumulative_co2 | float64 | 22848 | 45.32 | 23920 | 0.0 | 1849123.875 |
| cumulative_co2_including_luc | float64 | 26615 | 52.8 | 23641 | -120.345 | 2751504.25 |
| cumulative_coal_co2 | float64 | 28486 | 56.51 | 19139 | 0.0 | 849832.25 |
| cumulative_flaring_co2 | float64 | 34300 | 68.04 | 5673 | 0.0 | 20141.375 |
| cumulative_gas_co2 | float64 | 32264 | 64.0 | 9431 | 0.0 | 276572.6875 |
| cumulative_luc_co2 | float64 | 12961 | 25.71 | 35363 | -3918.0056 | 906953.5625 |
| cumulative_oil_co2 | float64 | 24953 | 49.5 | 20192 | 0.0 | 638014.1875 |
| cumulative_other_co2 | float64 | 47157 | 93.55 | 2201 | 0.0 | 14869.4033 |
| energy_per_capita | float64 | 39825 | 79.0 | 10500 | 0.0 | 318559.6875 |
| energy_per_gdp | float64 | 42624 | 84.55 | 7780 | 0.0 | 25.2525 |
| flaring_co2 | float64 | 34237 | 67.92 | 5366 | 0.0 | 432.3919 |
| flaring_co2_per_capita | float64 | 35501 | 70.42 | 5748 | 0.0 | 114.5091 |
| gas_co2 | float64 | 32264 | 64.0 | 8270 | 0.0 | 8009.8276 |
| gas_co2_per_capita | float64 | 32965 | 65.39 | 9809 | 0.0 | 53.4757 |
| ghg_excluding_lucf_per_capita | float64 | 14569 | 28.9 | 35830 | 0.0221 | 369.6498 |
| ghg_per_capita | float64 | 14232 | 28.23 | 36167 | -28.8521 | 369.7053 |
| land_use_change_co2 | float64 | 12961 | 25.71 | 32760 | -319.4175 | 8692.7666 |
| land_use_change_co2_per_capita | float64 | 13776 | 27.33 | 35080 | -45.3172 | 305.1949 |
| methane | float64 | 12261 | 24.32 | 38142 | 0.0001 | 9498.9141 |
| methane_per_capita | float64 | 14232 | 28.23 | 36168 | 0.0318 | 133.1039 |
| nitrous_oxide | float64 | 11911 | 23.63 | 37983 | 0.0 | 2935.7786 |
| nitrous_oxide_per_capita | float64 | 13972 | 27.72 | 35997 | 0.0 | 20.393 |
| oil_co2 | float64 | 24952 | 49.5 | 14443 | 0.0 | 12470.5957 |
| oil_co2_per_capita | float64 | 25689 | 50.96 | 21667 | 0.0 | 782.7434 |
| other_co2_per_capita | float64 | 47752 | 94.73 | 2550 | 0.0 | 0.6043 |
| other_industry_co2 | float64 | 47157 | 93.55 | 2085 | 0.0 | 458.1777 |
| primary_energy_consumption | float64 | 39780 | 78.91 | 10267 | 0.0 | 176737.0938 |
| share_global_cement_co2 | float64 | 28141 | 55.82 | 12455 | 0.0 | 100.0 |
| share_global_co2 | float64 | 22848 | 45.32 | 24946 | 0.0 | 100.0 |
| share_global_co2_including_luc | float64 | 26615 | 52.8 | 23523 | -0.3749 | 100.0 |
| share_global_coal_co2 | float64 | 28486 | 56.51 | 18559 | 0.0 | 100.0 |
| share_global_cumulative_cement_co2 | float64 | 28141 | 55.82 | 13126 | 0.0 | 100.0 |
| share_global_cumulative_co2 | float64 | 22848 | 45.32 | 25802 | 0.0 | 100.0 |
| share_global_cumulative_co2_including_luc | float64 | 26615 | 52.8 | 23579 | -0.1015 | 100.0 |
| share_global_cumulative_coal_co2 | float64 | 28486 | 56.51 | 20127 | 0.0 | 100.0 |
| share_global_cumulative_flaring_co2 | float64 | 39322 | 78.0 | 6029 | 0.0 | 100.0 |
| share_global_cumulative_gas_co2 | float64 | 35244 | 69.91 | 9734 | 0.0 | 100.0 |
| share_global_cumulative_luc_co2 | float64 | 12961 | 25.71 | 35640 | -0.5184 | 100.0 |
| share_global_cumulative_oil_co2 | float64 | 26578 | 52.72 | 21654 | 0.0 | 100.0 |
| share_global_cumulative_other_co2 | float64 | 48241 | 95.7 | 2001 | 0.0 | 100.0 |
| share_global_flaring_co2 | float64 | 39322 | 78.0 | 5580 | 0.0 | 100.0 |
| share_global_gas_co2 | float64 | 35244 | 69.91 | 9295 | 0.0 | 100.0 |
| share_global_luc_co2 | float64 | 12961 | 25.71 | 35394 | -6.9658 | 100.0 |
| share_global_oil_co2 | float64 | 26578 | 52.72 | 20629 | 0.0 | 100.0 |
| share_global_other_co2 | float64 | 48241 | 95.7 | 1999 | 0.0 | 100.0 |
| share_of_temperature_change_from_ghg | float64 | 9173 | 18.2 | 38975 | -0.8239 | 100.0 |
| temperature_change_from_ch4 | float64 | 12131 | 24.06 | 37930 | -0.0009 | 0.3765 |
| temperature_change_from_co2 | float64 | 9173 | 18.2 | 37311 | -0.0001 | 1.2164 |
| temperature_change_from_ghg | float64 | 9173 | 18.2 | 38930 | -0.0006 | 1.6784 |
| temperature_change_from_n2o | float64 | 12131 | 24.06 | 37765 | 0.0 | 0.0855 |
| total_ghg | float64 | 12261 | 24.32 | 38141 | -19.7252 | 54433.3984 |
| total_ghg_excluding_lucf | float64 | 12598 | 24.99 | 37810 | 0.0001 | 43714.7773 |
| trade_co2 | float64 | 45699 | 90.65 | 4575 | -2177.8074 | 1768.8463 |
| trade_co2_share | float64 | 45699 | 90.65 | 4605 | -98.2811 | 1023.0424 |
