CREATE OR REPLACE VIEW analytics.event_counts_by_category_and_city AS
SELECT
    city,
    category,
    COUNT(*) AS event_count
FROM public.events
WHERE city IS NOT NULL
  AND category IS NOT NULL
GROUP BY
    city,
    category;


SELECT *
FROM analytics.event_counts_by_category_and_city
ORDER BY event_count DESC;


SELECT
    city,
    category,
    event_count,
ROW_NUMBER() OVER (
    PARTITION BY city
    ORDER BY event_count DESC, category ASC
) AS category_rank
FROM analytics.event_counts_by_category_and_city;