-- What is a CTE?

-- CTE stands for: Common Table Expression ( Temporary Named Result)
-- Think of it like a temporary table that exists only while the query is running.

-- Think in Python suppose you have this:
-- events = load_events()
-- ranked_events = rank_events(events)
-- top_events = ranked_events[ranked_events.rank <= 3]

-- Notice how you broke the work into steps.
-- Each variable stores the result of the previous step. A CTE is the SQL equivalent.
-- WITH ranked_categories AS (...) means: Create a temporary table called ranked_categories.

WITH ranked_categories AS (
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
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY city, category_rank;