# File Format Comparison

- Generated (UTC): 2026-10-05T03:06:13+00:00
- Input: `global_power_plant_database.csv`
- Rows x columns: 34,936 x 36
- Timing: median of 3 runs
- Subset read: columns country, primary_fuel, capacity_mw

| format | size (MB) | vs CSV | write (s) | read all (s) | read subset (s) | dtype mismatches |
|---|---|---|---|---|---|---|
| csv | 11.345 | 1.00x | 0.5241 | 0.2763 | 0.099 | 0 |
| json | 38.937 | 3.43x | 0.3078 | 0.5709 | 0.6544 | 0 |
| parquet | 2.658 | 0.23x | 0.1006 | 0.0216 | 0.0105 | 0 |

## Observations

- Smallest file: parquet (2.658 MB).
- Fastest full read: parquet (0.0216 s).
- Fastest subset read: parquet (0.0105 s).

- csv: schema preserved for all columns.
- json: schema preserved for all columns.
- parquet: schema preserved for all columns.

## Trade-offs

- CSV: plain text, universally readable, no schema; types are re-inferred on every read, so dates and codes can change type; the whole file is parsed even when few columns are needed.
- JSON: self-describing and suitable for API payloads, but repeats every field name on every record, giving the largest files and slowest reads; no native date or integer/float distinction guarantees.
- Parquet: columnar and compressed, stores the schema, reads selected columns without parsing the rest, and supports partitioned datasets; requires a library (pyarrow) and is not human-readable.
