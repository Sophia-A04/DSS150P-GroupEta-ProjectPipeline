import pandas as pd
import pytest


@pytest.fixture
def wri_df():
    n = 10_000
    fuels = ["Coal", "Gas", "Hydro", "Solar", "Wind"]
    return pd.DataFrame({
        "country": ["PHL"] + ["USA"] * (n - 1),
        "country_long": ["Philippines"] + ["United States of America"] * (n - 1),
        "name": [f"Plant {i}" for i in range(n)],
        "gppd_idnr": [f"GPPD{i:07d}" for i in range(n)],
        "capacity_mw": [100.0 + i % 500 for i in range(n)],
        "latitude": [10.0] * n,
        "longitude": [120.0] * n,
        "primary_fuel": [fuels[i % 5] for i in range(n)],
        "commissioning_year": [2000.0] * n,
        "owner": ["Owner"] * n,
        "source": ["Source"] * n,
        "generation_gwh_2019": [50.0] * n,
    })


@pytest.fixture
def owid_df():
    countries, years = 100, 100
    rows = []
    for i in range(countries):
        iso = "PHL" if i == 0 else f"{chr(65 + i // 26)}{chr(65 + i % 26)}X"
        for y in range(1925, 1925 + years):
            rows.append({"country": f"Country {i}", "year": y, "iso_code": iso,
                         "population": 1_000_000.0, "gdp": 1e10, "co2": 10.0,
                         "co2_per_capita": 1.0, "coal_co2": 2.0, "methane": 3.0,
                         "share_global_co2": 0.5})
    return pd.DataFrame(rows)


@pytest.fixture
def wb_df():
    codes = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "NY.GDP.PCAP.CD"]
    isos = ["PHL"] + [f"{chr(65 + i // 26)}{chr(65 + i % 26)}X" for i in range(264)]
    rows = []
    for code in codes:
        for i, iso in enumerate(isos):
            rows.append({"indicator_id": code, "indicator_value": code,
                         "country_id": f"C{i}", "country_value": f"Country {i}",
                         "countryiso3code": iso, "date": "2019", "value": 1000.0 + i})
    return pd.DataFrame(rows)