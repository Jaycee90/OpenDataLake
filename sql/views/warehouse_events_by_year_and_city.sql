CREATE OR REPLACE VIEW analytics.warehouse_events_by_year_and_city AS
SELECT
    EXTRACT(YEAR FROM d.full_date)::INT AS event_year,
    v.city,
    COUNT(*) AS total_events
FROM analytics.fact_events AS f
JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key
JOIN analytics.dim_venue AS v
    ON f.venue_key = v.venue_key
GROUP BY
    EXTRACT(YEAR FROM d.full_date),
    v.city;

SELECT *
FROM analytics.warehouse_events_by_year_and_city
ORDER BY event_year DESC, total_events DESC;