CREATE OR REPLACE VIEW analytics.warehouse_events_by_month_and_city AS
SELECT
    MAKE_DATE(d.year, d.month, 1) AS event_month,
    v.city,
    COUNT(*) AS total_events
FROM analytics.fact_events AS f
JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key
JOIN analytics.dim_venue AS v
    ON f.venue_key = v.venue_key
GROUP BY
    d.year,
    d.month,
    v.city;