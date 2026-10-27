CREATE OR REPLACE VIEW analytics.warehouse_events_by_city AS
SELECT
    TRIM(v.city) AS city,
    COUNT(*) AS total_events
FROM analytics.fact_events AS f
JOIN analytics.dim_venue AS v
    ON f.venue_key = v.venue_key
GROUP BY TRIM(v.city);


SELECT *
FROM analytics.warehouse_events_by_city
ORDER BY total_events DESC;