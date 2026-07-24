CREATE OR REPLACE VIEW analytics.event_counts_by_venue AS
SELECT
    venue,
    COUNT(*) AS event_count
FROM public.events
WHERE venue IS NOT NULL
GROUP BY venue