CREATE OR REPLACE VIEW analytics.event_date_coverage AS
SELECT
    MIN(d.full_date) AS earliest_event_date,
    MAX(d.full_date) AS latest_event_date,
    COUNT(*) AS total_events
FROM analytics.fact_events AS f
JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key;

SELECT *
FROM analytics.event_date_coverage