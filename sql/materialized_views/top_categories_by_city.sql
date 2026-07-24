CREATE MATERIALIZED VIEW analytics.top_categories_by_city AS
WITH ranked_events_by_city_and_category AS (
    SELECT
        city,
        category,
        event_count,
        ROW_NUMBER() OVER (
            PARTITION BY city
            ORDER BY event_count DESC, category ASC
        ) AS category_rank
    FROM analytics.event_counts_by_category_and_city
)
SELECT
    city,
    category,
    event_count,
    category_rank
FROM ranked_events_by_city_and_category
WHERE category_rank <= 3;

SELECT *
FROM analytics.top_categories_by_city;