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

## Planned API contract

- `GET /api/health`: service status, sampling interval, last successful sample time.
- `GET /api/metrics/current`: the most recent collected sample, or 503 if unavailable.
- `GET /api/metrics/history?from=...&to=...&limit=720`: the latest matching samples
  displayed oldest first. Default range: last hour. Limit: 1–2000.
- History times must include a timezone; invalid inputs return 422.

A sample has a UTC timestamp, CPU/memory/root-disk percentages, uptime in seconds,
and a nullable CPU temperature in Celsius. Unsupported sensors return null.

## Planned storage

`metric_samples` has a UTC timestamp primary key and one numeric column per metric.
The collector will sample every five seconds. Each write will remove samples older
than 24 hours and keep at most 20,000 rows. SQLite is a local file excluded from Git.

## Development workflow

Make one understandable change, run its relevant checks, update the progress log,
commit with a descriptive message, and push. The initial prototype is Codex-assisted;
understanding and personal contributions should be recorded accurately.
