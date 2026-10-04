import pandas as pd


def iso_codes(n):
    return ["PHL", "USA"] + [f"{chr(65 + i // 26)}{chr(65 + i % 26)}X" for i in range(n - 2)]


def build_staging_plants(n=10_000):
    fuels = ["Coal", "Gas", "Hydro", "Solar", "Wind"]
    return pd.DataFrame({
        "country": ["PHL"] + ["USA"] * (n - 1),
        "country_long": ["Philippines"] + ["United States of America"] * (n - 1),
        "name": [f"Plant {i}" for i in range(n)],
        "gppd_idnr": [f"GPPD{i:07d}" for i in range(n)],
        "capacity_mw": [100.0 + i % 500 for i in range(n)],
        "primary_fuel": [fuels[i % 5] for i in range(n)],
        "latitude": [10.0] * n,
        "longitude": [120.0] * n,
    })


def build_staging_owid(n=217):
    isos = iso_codes(n)
    return pd.DataFrame({
        "owid_country": [f"Country {i}" for i in range(n)],
        "iso_code": isos,
        "year": [2019] * n,
        "co2": [10.0] * n,
        "co2_per_capita": [1.0] * n,
    })


def build_staging_wb(n=217):
    isos = iso_codes(n)
    return pd.DataFrame({
        "iso_code": isos,
        "wb_country": [f"Country {i}" for i in range(n)],
        "wb_year": ["2019"] * n,
        "wb_gdp_current_usd": [1e10] * n,
        "wb_population": [1_000_000.0] * n,
        "wb_gdp_per_capita_current_usd": [5000.0] * n,
    })