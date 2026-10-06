-- ============================================================
-- GROUP ETA
-- PHILIPPINES CONTEXT ANALYSIS
-- Snapshot: 2019
-- ============================================================


-- 1. PHILIPPINE POWER-PLANT SUMMARY
SELECT
    COUNT(*) AS plant_count,
    ROUND(
        SUM(capacity_mw)::NUMERIC,
        2
    ) AS total_installed_capacity_mw,
    ROUND(
        AVG(capacity_mw)::NUMERIC,
        2
    ) AS average_plant_capacity_mw
FROM power_plants
WHERE country_code = 'PHL';


-- 2. INSTALLED CAPACITY BY PRIMARY FUEL
SELECT
    f.fuel_name,
    f.fuel_group,
    fc.plant_count,
    ROUND(
        fc.installed_capacity_mw::NUMERIC,
        2
    ) AS installed_capacity_mw,
    ROUND(
        fc.capacity_share_pct::NUMERIC,
        2
    ) AS capacity_share_pct
FROM country_fuel_capacity fc
JOIN fuel_types f
    ON fc.fuel_id = f.fuel_id
WHERE fc.country_code = 'PHL'
  AND fc.snapshot_year = 2019
ORDER BY
    fc.installed_capacity_mw DESC;


-- 3. FOSSIL VS RENEWABLE VS OTHER CAPACITY
SELECT
    f.fuel_group,
    SUM(fc.plant_count) AS plant_count,
    ROUND(
        SUM(fc.installed_capacity_mw)::NUMERIC,
        2
    ) AS installed_capacity_mw,
    ROUND(
        (
            SUM(fc.installed_capacity_mw)
            /
            SUM(
                SUM(fc.installed_capacity_mw)
            ) OVER ()
            * 100
        )::NUMERIC,
        2
    ) AS installed_capacity_share_pct
FROM country_fuel_capacity fc
JOIN fuel_types f
    ON fc.fuel_id = f.fuel_id
WHERE fc.country_code = 'PHL'
  AND fc.snapshot_year = 2019
GROUP BY
    f.fuel_group
ORDER BY
    installed_capacity_mw DESC;


-- 4. PHILIPPINE EMISSIONS + ECONOMIC CONTEXT
SELECT
    c.country_name,
    e.year,
    ROUND(
        e.co2::NUMERIC,
        3
    ) AS co2,
    ROUND(
        e.co2_per_capita::NUMERIC,
        3
    ) AS co2_per_capita,
    ROUND(
        w.gdp_current_usd::NUMERIC,
        2
    ) AS gdp_current_usd,
    w.population,
    ROUND(
        w.gdp_per_capita_current_usd::NUMERIC,
        2
    ) AS gdp_per_capita_current_usd
FROM countries c
LEFT JOIN country_emissions e
    ON c.country_code = e.country_code
    AND e.year = 2019
LEFT JOIN country_economic_indicators w
    ON c.country_code = w.country_code
    AND w.year = 2019
WHERE c.country_code = 'PHL';


-- 5. TEN LARGEST PHILIPPINE POWER PLANTS
SELECT
    p.plant_name,
    f.fuel_name AS primary_fuel,
    ROUND(
        p.capacity_mw::NUMERIC,
        2
    ) AS capacity_mw,
    p.commissioning_year
FROM power_plants p
JOIN fuel_types f
    ON p.primary_fuel_id = f.fuel_id
WHERE p.country_code = 'PHL'
ORDER BY
    p.capacity_mw DESC
LIMIT 10;


-- 6. PHILIPPINE SHARE OF GLOBAL DATABASE CAPACITY
SELECT
    ROUND(
        (
            SUM(
                CASE
                    WHEN country_code = 'PHL'
                    THEN capacity_mw
                    ELSE 0
                END
            )
            /
            SUM(capacity_mw)
            * 100
        )::NUMERIC,
        4
    ) AS philippines_share_of_database_capacity_pct
FROM power_plants;