CREATE OR REPLACE VIEW analytics.upcoming_events AS
SELECT *
FROM public.events
WHERE event_date >= CURRENT_DATE
  AND status IS DISTINCT FROM 'cancelled';