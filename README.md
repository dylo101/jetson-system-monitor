# Jetson System Monitor

A learning project for a Linux host monitoring API and browser dashboard.

## Build checkpoints

1. Establish the folder structure and API contract.
2. Collect host metrics and expose a tested FastAPI API.
3. Save samples in SQLite and query bounded history.
4. Add a React/TypeScript dashboard and explain the data flow.

Each checkpoint is a separate Git commit pushed to GitHub after its checks pass.
Use small, descriptive commits for future work too. Commit source and tests;
exclude dependencies, databases, secrets, and host readings.

```text
backend/app/      Python API, collector, and storage
backend/tests/    Automated behavior tests
frontend/src/     Browser dashboard
docs/            Architecture and evidence of progress
```

The prototype is separate from other host applications and collects only ordinary
system metrics. Development servers will bind to loopback.

## Backend setup

From the repository root (Python 3.10+ required):

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e './backend[dev]'
cd backend
.venv/bin/pytest -q
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The virtual environment keeps Python dependencies local to this project. Pytest
checks behavior; Uvicorn runs the API until you press Ctrl+C. Open
http://127.0.0.1:8000/docs to explore the API.

`SAMPLE_INTERVAL_SECONDS` controls the pause between samples (default 5, allowed
1–3600). CPU readings measure a short 0.1-second window. Temperature is null when
no CPU-labelled sensor is available. Failed collection retains the previous
reading and marks health degraded. Before the first successful sample, current
metrics returns 503. Run only one API worker so there is only one sampler.

## History

`GET /api/metrics/history` returns the last hour of stored samples (up to 720).
Optional `from` and `to` parameters accept ISO timestamps with a timezone, and
`limit` accepts 1–2000. Results contain the newest matching samples in ascending
time order. Invalid ranges return HTTP 422.

`DATABASE_PATH` overrides the default `backend/data/metrics.sqlite3`. A successful
sample is saved before it appears in the current endpoint. Each write removes
samples older than 24 hours and caps the table at 20,000 rows. SQLite reuses freed
pages rather than immediately shrinking its file. Databases are excluded from Git.

## Dashboard setup

With the backend running, open another terminal at the repository root. Requires
Node 20.19+ or 22.12+ (Node 24 is supported).

```bash
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173 on the machine running the servers. Vite serves the
frontend and proxies `/api` requests to the backend at port 8000. Stop either
server with Ctrl+C; these are development processes, not persistent services.

For a browser on your own computer connected to the Jetson by SSH:

```bash
ssh -L 5173:127.0.0.1:5173 -L 8000:127.0.0.1:8000 YOUR_USER@YOUR_JETSON
```

Then open the same localhost URL on your computer. This forwards loopback ports
without exposing development servers on the network.

To check TypeScript and build frontend assets, run `npm run build` from `frontend/`.
The dashboard refreshes every five seconds and shows current cards plus a CPU
history chart. It retains previous readings during connection failures and marks
samples stale after three sampling intervals (at least 15 seconds). Loading,
empty-history, and unsupported-temperature states have dedicated messages.

## Understand the code

Read `backend/app/models.py` → `metrics.py` → `db.py` → `main.py`, then
`frontend/src/main.tsx`. See [the walkthrough](docs/architecture.md) and
[the progress log](docs/progress-log.md).

The prototype has no GPU metrics, authentication, production hosting, CI, or
Docker packaging. The frontend build checks types and packaging; it is not an
automated browser test. Backend tests use temporary databases and fake readings.
The current dependency versions emit a TestClient/httpx deprecation warning;
the tests still run successfully. Initial code was generated with Codex assistance.
