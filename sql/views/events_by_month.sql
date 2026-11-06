CREATE OR REPLACE VIEW analytics.warehouse_events_by_month AS
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS total_events,
    MAKE_DATE(d.year, d.month, 1) AS event_month
FROM analytics.fact_events AS f
JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name;

SELECT *
FROM analytics.warehouse_events_by_month
ORDER BY year, month;