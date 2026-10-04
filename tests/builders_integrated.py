from tests.builders import build_staging_plants


def build_integrated(n=10_000):
    df = build_staging_plants(n)
    df["total_installed_capacity_mw"] = df.groupby("country")["capacity_mw"].transform("sum")
    df["country_primary_fuel_capacity_mw"] = df.groupby(["country", "primary_fuel"])["capacity_mw"].transform("sum")
    df["country_primary_fuel_capacity_share_pct"] = (
        df["country_primary_fuel_capacity_mw"] / df["total_installed_capacity_mw"] * 100)
    df["fossil_share_pct"] = 40.0
    df["renewable_share_pct"] = 50.0
    df["owid_country"] = "Country"
    df["co2"] = 10.0
    df["co2_per_capita"] = 1.0
    df["owid_2019_matched"] = True
    df["wb_gdp_current_usd"] = 1e10
    df["wb_population"] = 1_000_000.0
    df["wb_gdp_per_capita_current_usd"] = 5000.0
    df["wb_2019_matched"] = True
    return df