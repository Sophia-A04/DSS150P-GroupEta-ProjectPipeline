CREATE TABLE IF NOT EXISTS countries (
    country_code CHAR(3) PRIMARY KEY,
    country_name TEXT NOT NULL,
    owid_country_name TEXT,
    wb_country_name TEXT,

    CONSTRAINT chk_country_code_length
        CHECK (char_length(country_code) = 3)
);


CREATE TABLE IF NOT EXISTS fuel_types (
    fuel_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fuel_name VARCHAR(50) NOT NULL UNIQUE,
    fuel_group VARCHAR(30) NOT NULL,

    CONSTRAINT chk_fuel_group
        CHECK (
            fuel_group IN (
                'fossil',
                'renewable',
                'other_or_unclassified'
            )
        )
);


CREATE TABLE IF NOT EXISTS power_plants (
    gppd_idnr VARCHAR(50) PRIMARY KEY,
    country_code CHAR(3) NOT NULL,
    plant_name TEXT NOT NULL,
    capacity_mw DOUBLE PRECISION NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    primary_fuel_id SMALLINT NOT NULL,
    other_fuel1 VARCHAR(50),
    other_fuel2 VARCHAR(50),
    other_fuel3 VARCHAR(50),
    commissioning_year SMALLINT,
    owner TEXT,
    source TEXT,
    source_url TEXT,
    geolocation_source TEXT,
    wepp_id TEXT,
    year_of_capacity_data SMALLINT,

    CONSTRAINT fk_power_plants_country
        FOREIGN KEY (country_code)
        REFERENCES countries(country_code),

    CONSTRAINT fk_power_plants_fuel
        FOREIGN KEY (primary_fuel_id)
        REFERENCES fuel_types(fuel_id),

    CONSTRAINT chk_capacity_positive
        CHECK (capacity_mw > 0),

    CONSTRAINT chk_latitude
        CHECK (
            latitude IS NULL
            OR latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT chk_longitude
        CHECK (
            longitude IS NULL
            OR longitude BETWEEN -180 AND 180
        )
);


CREATE TABLE IF NOT EXISTS plant_generation (
    gppd_idnr VARCHAR(50) NOT NULL,
    generation_year SMALLINT NOT NULL,
    generation_gwh DOUBLE PRECISION,
    estimated_generation_gwh DOUBLE PRECISION,
    generation_data_source TEXT,
    estimation_note TEXT,

    PRIMARY KEY (
        gppd_idnr,
        generation_year
    ),

    CONSTRAINT fk_generation_plant
        FOREIGN KEY (gppd_idnr)
        REFERENCES power_plants(gppd_idnr)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS country_emissions (
    country_code CHAR(3) NOT NULL,
    year SMALLINT NOT NULL,
    co2 DOUBLE PRECISION,
    co2_per_capita DOUBLE PRECISION,
    coal_co2 DOUBLE PRECISION,
    gas_co2 DOUBLE PRECISION,
    oil_co2 DOUBLE PRECISION,
    methane DOUBLE PRECISION,
    nitrous_oxide DOUBLE PRECISION,
    total_ghg DOUBLE PRECISION,
    primary_energy_consumption DOUBLE PRECISION,
    share_global_co2 DOUBLE PRECISION,

    PRIMARY KEY (
        country_code,
        year
    ),

    CONSTRAINT fk_emissions_country
        FOREIGN KEY (country_code)
        REFERENCES countries(country_code)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS country_economic_indicators (
    country_code CHAR(3) NOT NULL,
    year SMALLINT NOT NULL,
    gdp_current_usd NUMERIC(24, 2),
    population BIGINT,
    gdp_per_capita_current_usd NUMERIC(18, 4),

    PRIMARY KEY (
        country_code,
        year
    ),

    CONSTRAINT fk_economic_country
        FOREIGN KEY (country_code)
        REFERENCES countries(country_code)
        ON DELETE CASCADE,

    CONSTRAINT chk_population_nonnegative
        CHECK (
            population IS NULL
            OR population >= 0
        )
);


CREATE TABLE IF NOT EXISTS country_fuel_capacity (
    country_code CHAR(3) NOT NULL,
    fuel_id SMALLINT NOT NULL,
    snapshot_year SMALLINT NOT NULL,
    plant_count INTEGER NOT NULL,
    installed_capacity_mw DOUBLE PRECISION NOT NULL,
    capacity_share_pct DOUBLE PRECISION NOT NULL,

    PRIMARY KEY (
        country_code,
        fuel_id,
        snapshot_year
    ),

    CONSTRAINT fk_capacity_country
        FOREIGN KEY (country_code)
        REFERENCES countries(country_code)
        ON DELETE CASCADE,

    CONSTRAINT fk_capacity_fuel
        FOREIGN KEY (fuel_id)
        REFERENCES fuel_types(fuel_id),

    CONSTRAINT chk_plant_count_nonnegative
        CHECK (plant_count >= 0),

    CONSTRAINT chk_installed_capacity_nonnegative
        CHECK (installed_capacity_mw >= 0),

    CONSTRAINT chk_capacity_share
        CHECK (
            capacity_share_pct
            BETWEEN 0 AND 100.01
        )
);


CREATE INDEX IF NOT EXISTS idx_power_plants_country
    ON power_plants(country_code);

CREATE INDEX IF NOT EXISTS idx_power_plants_fuel
    ON power_plants(primary_fuel_id);

CREATE INDEX IF NOT EXISTS idx_emissions_year
    ON country_emissions(year);

CREATE INDEX IF NOT EXISTS idx_economic_year
    ON country_economic_indicators(year);

CREATE INDEX IF NOT EXISTS idx_capacity_country
    ON country_fuel_capacity(country_code);

CREATE INDEX IF NOT EXISTS idx_capacity_year
    ON country_fuel_capacity(snapshot_year);