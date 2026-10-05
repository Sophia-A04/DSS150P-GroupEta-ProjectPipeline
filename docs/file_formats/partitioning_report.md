# Partitioning Report

- Generated (UTC): 2026-10-05T10:38:22+00:00
- Input: `global_power_plant_database.csv`
- Partition key: `country` (Hive-style directories, Parquet files)
- Partitions: 167 for 34,936 rows
- Largest partition: USA (9,833 rows)
- Smallest partition: DJI (1 rows)

## Selective read: PHL

| method | seconds | rows returned | files read |
|---|---|---|---|
| full scan then filter | 0.2381 | 123 | all |
| partition read | 0.0351 | 123 | 1 of 167 |

Partition pruning reads 1 of 167 files (6.8x faster than the full scan in this run).

## Rationale for the partition key

- `country` (ISO-3) is the join key to OWID and World Bank and the unit of analysis: national power-generation profiles, fuel-mix clustering and Philippine-specific findings all filter or aggregate by country.
- Cardinality is moderate (about 160 to 170 values), so a country query reads one small partition while the number of files stays manageable.
- Partitions are uneven (a few countries hold thousands of plants, many hold only a handful); this is accepted because queries are country-first and every partition remains small in absolute size.
- Alternatives considered: `primary_fuel` (15 balanced values, but analysis is not fuel-first), `commissioning_year` (many missing values, so nulls would need a separate partition), and no partitioning (every Philippine query would scan all plants).
- Rerun safety: the target directory is replaced on every write, so repeated runs never duplicate files or rows.
