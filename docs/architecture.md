# Prototype design

```text
Linux → psutil collector → validated sample → SQLite
                                ↓               ↓
                         current endpoint   history endpoint
                                ↓               ↓
                              React dashboard
```

FastAPI handles HTTP requests. A separate collector reads system metrics. A
repository owns SQL queries. React presents results and refreshes them periodically.
SQLite keeps the prototype easy to run without a separate database service.

## API contract

- `GET /api/health`: service status, sampling interval, last successful sample time.
- `GET /api/metrics/current`: the most recent collected sample, or 503 if unavailable.
- `GET /api/metrics/history?from=...&to=...&limit=720`: the latest matching samples
  displayed oldest first. Default range: last hour. Limit: 1–2000.
- History times must include a timezone; invalid inputs return 422.

A sample has a UTC timestamp, CPU/memory/root-disk percentages, uptime in seconds,
and a nullable CPU temperature in Celsius. Unsupported sensors return null.

## Storage

`metric_samples` has a UTC timestamp primary key and one numeric column per metric.
The collector samples every five seconds by default. Each write removes samples older
than 24 hours and keep at most 20,000 rows. SQLite is a local file excluded from Git.

## Development workflow

Make one understandable change, run its relevant checks, update the progress log,
commit with a descriptive message, and push. The initial prototype is Codex-assisted;
understanding and personal contributions should be recorded accurately.

## Follow one reading from Linux to the screen

1. `SystemMetrics.collect()` in `metrics.py` reads CPU, memory, disk, uptime, and
   any available CPU temperature using psutil. These are read-only system queries.
2. `MetricSample` in `models.py` validates the shape and ranges of those values.
   A missing temperature becomes null, rather than a made-up number.
3. The background task in `main.py` saves each sample through `Repository.save()`
   in `db.py`. SQL inserts the row and removes old or excess rows in one transaction.
4. The API caches the latest saved sample in memory. The current endpoint returns
   it quickly; the history endpoint queries the database. Historical readings
   survive restarts because SQLite stores them in a file.
5. `App()` in `frontend/src/main.tsx` fetches the three endpoints every five seconds.
   React state holds the responses; changing state redraws the metric cards.
6. `CpuChart()` maps timestamps to horizontal positions and CPU percentages to
   vertical positions. SVG draws the line without a separate chart library.

## Why these choices?

Separate collector, storage, and HTTP code lets tests replace the real collector
with a predictable fake. This is dependency injection: supplying a dependency
instead of constructing it inside every function that needs it. Temporary SQLite
databases let tests check storage without changing real history.

SQLite avoids a separate server and raw SQL makes the queries visible. React and
TypeScript add a build step but give us typed UI components. A simple SVG chart
needs little code, though a chart library would provide richer interactions.
The API performs collection in a worker thread so the short CPU measurement and
database write do not block its asynchronous event loop.

## Try a small change yourself

Open the API documentation at `/docs` and compare `/api/metrics/current` JSON with
the CPU card. Explain which JSON field supplies the number and where the percent
sign is added. Then change the card description and run `npm run build`.

Next, read the history SQL and explain why it selects descending timestamps but
returns rows in reverse order: the query chooses the newest limited set, then the
chart receives those samples oldest first.
