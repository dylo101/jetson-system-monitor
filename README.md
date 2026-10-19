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
