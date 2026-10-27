CREATE OR REPLACE VIEW analytics.warehouse_events_by_category AS
SELECT
    c.category,
    COUNT(*) AS total_events
FROM analytics.fact_events AS f
JOIN analytics.dim_category AS c
    ON f.category_key = c.category_key
GROUP BY c.category;

SELECT *
FROM analytics.warehouse_events_by_category
ORDER BY total_events DESC;

-- SELECT
--     city,
--     category,
--     event_count,
-- ROW_NUMBER() OVER (
--     PARTITION BY city
--     ORDER BY event_count DESC, category ASC
-- ) AS category_rank
-- FROM analytics.event_counts_by_category_and_city;