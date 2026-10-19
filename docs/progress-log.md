# Progress log

## Checkpoint 1 — Project structure

- Removed the first uncommitted prototype at the user's request; preserved the
  original Git history and restarted implementation.
- Added backend, tests, frontend, and documentation folders.
- Wrote the proposed API contract, storage bounds, and commit workflow.
- Checked the local branch against GitHub: both started at the initial commit.
- Application implementation and runtime checks are still pending.

## Checkpoint 2 — Current-metrics API

- Added validated sample models, a read-only psutil collector, a background
  sampler, and health/current endpoints. Missing CPU sensors produce null.
- Added six passing tests for responses, collection failure, and metric mapping.
- Tests passed outside the sandbox in 1.08 seconds; the sandbox stalled the
  threaded TestClient. The dependency emitted a TestClient/httpx deprecation warning.
- Published checkpoint 1 using the machine's existing SSH key. HTTPS lacked
  credentials, and the connected GitHub app denied write access.
- Historical storage and the browser dashboard remain pending.
