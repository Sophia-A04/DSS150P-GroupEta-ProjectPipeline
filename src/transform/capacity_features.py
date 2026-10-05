from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "country",
    "gppd_idnr",
    "capacity_mw",
    "primary_fuel",
]

FOSSIL_FUELS = {
    "Coal",
    "Gas",
    "Oil",
    "Petcoke",
}

RENEWABLE_FUELS = {
    "Biomass",
    "Geothermal",
    "Hydro",
    "Solar",
    "Wind",
    "Waste",
    "Wave and Tidal",
}


def _require_columns(df: pd.DataFrame) -> None:
    """Raise an error when required plant columns are missing."""
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Plant staging data is missing required columns: "
            + ", ".join(missing)
        )


def build_country_totals(
    plants: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build one row per country containing total plant count
    and total installed capacity.
    """
    _require_columns(plants)

    country_totals = (
        plants
        .groupby(
            "country",
            as_index=False,
        )
        .agg(
            total_plant_count=(
                "gppd_idnr",
                "nunique",
            ),
            total_installed_capacity_mw=(
                "capacity_mw",
                "sum",
            ),
        )
    )

    return country_totals


def build_country_fuel_capacity(
    plants: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build country + primary-fuel installed-capacity statistics.

    Output grain:
        one row = one country + primary fuel combination
    """
    _require_columns(plants)

    country_totals = build_country_totals(
        plants
    )

    country_fuel_capacity = (
        plants
        .groupby(
            [
                "country",
                "primary_fuel",
            ],
            as_index=False,
        )
        .agg(
            plant_count=(
                "gppd_idnr",
                "nunique",
            ),
            capacity_mw=(
                "capacity_mw",
                "sum",
            ),
        )
    )

    country_fuel_capacity = (
        country_fuel_capacity
        .merge(
            country_totals[
                [
                    "country",
                    "total_installed_capacity_mw",
                ]
            ],
            on="country",
            how="left",
            validate="many_to_one",
        )
    )

    country_fuel_capacity[
        "capacity_share_pct"
    ] = (
        country_fuel_capacity[
            "capacity_mw"
        ]
        / country_fuel_capacity[
            "total_installed_capacity_mw"
        ]
        * 100
    )

    return country_fuel_capacity


def build_country_capacity_features(
    plants: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build one row per country containing installed-capacity features.

    Includes:
    - total plant count
    - total installed capacity
    - installed capacity by primary fuel
    - installed-capacity share by primary fuel
    - fossil capacity and share
    - renewable capacity and share
    - other/unclassified capacity and share
    """
    _require_columns(plants)

    country_totals = build_country_totals(
        plants
    )

    country_fuel_capacity = (
        build_country_fuel_capacity(
            plants
        )
    )

    # Fuel-specific installed capacity.
    capacity_pivot = (
        country_fuel_capacity
        .pivot(
            index="country",
            columns="primary_fuel",
            values="capacity_mw",
        )
        .fillna(0)
    )

    capacity_pivot.columns = [
        f"{fuel}_capacity_mw"
        for fuel in capacity_pivot.columns
    ]

    capacity_pivot = (
        capacity_pivot
        .reset_index()
    )

    # Fuel-specific installed-capacity shares.
    share_pivot = (
        country_fuel_capacity
        .pivot(
            index="country",
            columns="primary_fuel",
            values="capacity_share_pct",
        )
        .fillna(0)
    )

    share_pivot.columns = [
        f"{fuel}_share_pct"
        for fuel in share_pivot.columns
    ]

    share_pivot = (
        share_pivot
        .reset_index()
    )

    country_capacity_profile = (
        country_totals
        .merge(
            capacity_pivot,
            on="country",
            how="left",
            validate="one_to_one",
        )
        .merge(
            share_pivot,
            on="country",
            how="left",
            validate="one_to_one",
        )
    )

    # Conservatively group fuels into fossil,
    # renewable, and other/unclassified.
    capacity_groups = plants[
        [
            "country",
            "gppd_idnr",
            "capacity_mw",
            "primary_fuel",
        ]
    ].copy()

    capacity_groups[
        "capacity_group"
    ] = np.select(
        [
            capacity_groups[
                "primary_fuel"
            ].isin(
                FOSSIL_FUELS
            ),
            capacity_groups[
                "primary_fuel"
            ].isin(
                RENEWABLE_FUELS
            ),
        ],
        [
            "fossil",
            "renewable",
        ],
        default="other_or_unclassified",
    )

    country_group_capacity = (
        capacity_groups
        .groupby(
            [
                "country",
                "capacity_group",
            ],
            as_index=False,
        )
        .agg(
            capacity_mw=(
                "capacity_mw",
                "sum",
            )
        )
    )

    country_group_profile = (
        country_group_capacity
        .pivot(
            index="country",
            columns="capacity_group",
            values="capacity_mw",
        )
        .fillna(0)
        .reset_index()
    )

    # Ensure all three group columns exist,
    # even if a dataset does not contain one group.
    for group in [
        "fossil",
        "renewable",
        "other_or_unclassified",
    ]:
        if (
            group
            not in country_group_profile.columns
        ):
            country_group_profile[
                group
            ] = 0.0

    country_group_profile = (
        country_group_profile
        .rename(
            columns={
                "fossil":
                    "fossil_capacity_mw",
                "renewable":
                    "renewable_capacity_mw",
                "other_or_unclassified":
                    "other_or_unclassified_capacity_mw",
            }
        )
    )

    country_group_profile = (
        country_group_profile
        .merge(
            country_totals[
                [
                    "country",
                    "total_installed_capacity_mw",
                ]
            ],
            on="country",
            how="left",
            validate="one_to_one",
        )
    )

    country_group_profile[
        "fossil_share_pct"
    ] = (
        country_group_profile[
            "fossil_capacity_mw"
        ]
        / country_group_profile[
            "total_installed_capacity_mw"
        ]
        * 100
    )

    country_group_profile[
        "renewable_share_pct"
    ] = (
        country_group_profile[
            "renewable_capacity_mw"
        ]
        / country_group_profile[
            "total_installed_capacity_mw"
        ]
        * 100
    )

    country_group_profile[
        "other_or_unclassified_share_pct"
    ] = (
        country_group_profile[
            "other_or_unclassified_capacity_mw"
        ]
        / country_group_profile[
            "total_installed_capacity_mw"
        ]
        * 100
    )

    # total_installed_capacity_mw already exists
    # in country_capacity_profile.
    country_group_profile = (
        country_group_profile
        .drop(
            columns=[
                "total_installed_capacity_mw"
            ]
        )
    )

    country_capacity_features = (
        country_capacity_profile
        .merge(
            country_group_profile,
            on="country",
            how="left",
            validate="one_to_one",
        )
    )

    return country_capacity_features


def add_capacity_features_to_plants(
    plants: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach country-level and country-primary-fuel
    capacity features back to individual plant records.

    The plant-level grain must be preserved:
        one row = one real power plant
    """
    _require_columns(plants)

    original_rows = len(plants)

    country_capacity_features = (
        build_country_capacity_features(
            plants
        )
    )

    country_fuel_capacity = (
        build_country_fuel_capacity(
            plants
        )
    )

    plant_fuel_features = (
        country_fuel_capacity[
            [
                "country",
                "primary_fuel",
                "plant_count",
                "capacity_mw",
                "capacity_share_pct",
            ]
        ]
        .rename(
            columns={
                "plant_count":
                    "country_primary_fuel_plant_count",
                "capacity_mw":
                    "country_primary_fuel_capacity_mw",
                "capacity_share_pct":
                    "country_primary_fuel_capacity_share_pct",
            }
        )
    )

    enriched = (
        plants
        .copy()
        .merge(
            country_capacity_features,
            on="country",
            how="left",
            validate="many_to_one",
        )
        .merge(
            plant_fuel_features,
            on=[
                "country",
                "primary_fuel",
            ],
            how="left",
            validate="many_to_one",
        )
    )

    if len(enriched) != original_rows:
        raise RuntimeError(
            "Capacity-feature merge changed the "
            "plant-level row count."
        )

    return enriched.reset_index(drop=True)