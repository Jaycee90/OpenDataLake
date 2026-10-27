CREATE MATERIALIZED VIEW analytics.top_categories_by_city AS
WITH category_counts AS (
    SELECT
        TRIM(v.city)::VARCHAR AS city,
        c.category,
        COUNT(*) AS event_count
    FROM analytics.fact_events AS f
    JOIN analytics.dim_venue AS v
        ON f.venue_key = v.venue_key
    JOIN analytics.dim_category AS c
        ON f.category_key = c.category_key
    GROUP BY TRIM(v.city), c.category
),
ranked_categories AS (
    SELECT
        city,
        category,
        event_count,
        ROW_NUMBER() OVER (
            PARTITION BY city
            ORDER BY event_count DESC, category ASC
        ) AS category_rank
    FROM category_counts
)
SELECT
    city,
    category,
    event_count,
    category_rank
FROM ranked_categories
WHERE category_rank <= 3;