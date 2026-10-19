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

## Checkpoint 3 — Persistent history

- Added a SQLite repository with UTC timestamps, parameterized range queries,
  24-hour retention, and a 20,000-row safety cap.
- Added a history endpoint with timezone, ordering, and result-limit validation.
- Expanded the test suite: nine tests passed in 2.35 seconds, including API
  restart persistence, database range/order behavior, retention, and row limits.
- Browser integration remains pending. The TestClient dependency warning remains.

## Checkpoint 4 — Dashboard and walkthrough

- Added React/TypeScript metric cards, a timestamp-based SVG CPU chart, polling,
  and loading, empty, unavailable, stale, and connection-error messages.
- Added project setup/run instructions, an SSH forwarding example, and a
  beginner-oriented walkthrough from collection through SQL to the screen.
- `npm run build` passed: TypeScript checking and Vite production bundling.
- Live HTTP smoke check passed through port 5173: frontend HTML, API proxy,
  health, real host readings, stored history, and a newer sample after six seconds.
- Browser automation timed out, so visual rendering and interactive browser
  behavior remain unverified. No automated frontend browser suite is present.
- Development preview runs on loopback ports 8000 and 5173; no persistent services
  were installed. Generated dependencies, build output, and real readings stay out
  of Git. The original external brief was not copied into the public repository.
- Next learning step: trace a JSON field into a card, make a small user-authored
  UI change, build it, and commit it as the next meaningful checkpoint.
