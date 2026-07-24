CREATE MATERIALIZED VIEW analytics.event_counts_by_city_and_month AS
SELECT
    city,
    DATE_TRUNC('month', event_date)::DATE AS event_month,
    COUNT(*) AS event_count
FROM public.events
WHERE city IS NOT NULL
  AND event_date IS NOT NULL
GROUP BY
    city,
    DATE_TRUNC('month', event_date);

SELECT *
FROM analytics.event_counts_by_city_and_month
ORDER BY event_month, city;