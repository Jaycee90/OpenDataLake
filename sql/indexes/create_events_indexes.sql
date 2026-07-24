-- PostgreSQL chooses the cheapest execution plan. It will decide whether to use indexes or just reading everything.
CREATE INDEX IF NOT EXISTS idx_events_city
ON public.events(city);

CREATE INDEX IF NOT EXISTS idx_events_venue
ON public.events(venue);

CREATE INDEX IF NOT EXISTS idx_events_event_date
ON public.events(event_date);



EXPLAIN ANALYZE
SELECT *
FROM public.events
WHERE city = 'Austin';