-- ============================================================
-- GROUP ETA
-- PostgreSQL Relationship Verification + Representative Queries
-- ============================================================


-- ------------------------------------------------------------
-- 1. FOREIGN-KEY / RELATIONSHIP INTEGRITY CHECKS
-- All orphan counts should equal 0.
-- ------------------------------------------------------------

SELECT
    'power_plants -> countries' AS relationship,
    COUNT(*) AS orphan_rows
FROM power_plants p
LEFT JOIN countries c
    ON p.country_code = c.country_code
WHERE c.country_code IS NULL

UNION ALL

SELECT
    'power_plants -> fuel_types',
    COUNT(*)
FROM power_plants p
LEFT JOIN fuel_types f
    ON p.primary_fuel_id = f.fuel_id
WHERE f.fuel_id IS NULL

UNION ALL

SELECT
    'plant_generation -> power_plants',
    COUNT(*)
FROM plant_generation g
LEFT JOIN power_plants p
    ON g.gppd_idnr = p.gppd_idnr
WHERE p.gppd_idnr IS NULL

UNION ALL

SELECT
    'country_emissions -> countries',
    COUNT(*)
FROM country_emissions e
LEFT JOIN countries c
    ON e.country_code = c.country_code
WHERE c.country_code IS NULL

UNION ALL

SELECT
    'country_economic_indicators -> countries',
    COUNT(*)
FROM country_economic_indicators e
LEFT JOIN countries c
    ON e.country_code = c.country_code
WHERE c.country_code IS NULL

UNION ALL

SELECT
    'country_fuel_capacity -> countries',
    COUNT(*)
FROM country_fuel_capacity fc
LEFT JOIN countries c
    ON fc.country_code = c.country_code
WHERE c.country_code IS NULL

UNION ALL

SELECT
    'country_fuel_capacity -> fuel_types',
    COUNT(*)
FROM country_fuel_capacity fc
LEFT JOIN fuel_types f
    ON fc.fuel_id = f.fuel_id
WHERE f.fuel_id IS NULL;


-- ------------------------------------------------------------
-- 2. PHILIPPINES INSTALLED CAPACITY BY FUEL
-- ------------------------------------------------------------

SELECT
    f.fuel_name,
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
ORDER BY fc.installed_capacity_mw DESC;


-- ------------------------------------------------------------
-- 3. PHILIPPINES COUNTRY + EMISSIONS + ECONOMIC DATA
-- ------------------------------------------------------------

SELECT
    c.country_code,
    c.country_name,
    e.year,
    e.co2,
    e.co2_per_capita,
    w.gdp_current_usd,
    w.population,
    w.gdp_per_capita_current_usd
FROM countries c
LEFT JOIN country_emissions e
    ON c.country_code = e.country_code
    AND e.year = 2019
LEFT JOIN country_economic_indicators w
    ON c.country_code = w.country_code
    AND w.year = 2019
WHERE c.country_code = 'PHL';


-- ------------------------------------------------------------
-- 4. TOP 10 COUNTRIES BY INSTALLED CAPACITY
-- ------------------------------------------------------------

SELECT
    c.country_code,
    c.country_name,
    ROUND(
        SUM(fc.installed_capacity_mw)::NUMERIC,
        2
    ) AS total_installed_capacity_mw
FROM country_fuel_capacity fc
JOIN countries c
    ON fc.country_code = c.country_code
WHERE fc.snapshot_year = 2019
GROUP BY
    c.country_code,
    c.country_name
ORDER BY
    total_installed_capacity_mw DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 5. PHILIPPINES REPORTED GENERATION IN 2019
-- ------------------------------------------------------------

SELECT
    COUNT(DISTINCT p.gppd_idnr)
        AS plants_with_generation_records,
    ROUND(
        SUM(g.generation_gwh)::NUMERIC,
        2
    ) AS total_reported_generation_gwh
FROM plant_generation g
JOIN power_plants p
    ON g.gppd_idnr = p.gppd_idnr
WHERE p.country_code = 'PHL'
  AND g.generation_year = 2019;


-- ------------------------------------------------------------
-- 6. SAMPLE PHILIPPINE POWER PLANTS
-- ------------------------------------------------------------

SELECT
    p.gppd_idnr,
    p.plant_name,
    f.fuel_name AS primary_fuel,
    p.capacity_mw,
    p.commissioning_year
FROM power_plants p
JOIN fuel_types f
    ON p.primary_fuel_id = f.fuel_id
WHERE p.country_code = 'PHL'
ORDER BY p.capacity_mw DESC
LIMIT 10;