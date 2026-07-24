CREATE OR REPLACE VIEW analytics.event_counts_by_city AS
SELECT
    city,
    COUNT(*) AS event_count
FROM public.events
WHERE city IS NOT NULL
GROUP BY city;


SELECT *
FROM analytics.event_counts_by_venue
ORDER BY event_count DESC;