import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from app.metrics import SystemMetrics
from app.models import MetricSample
from app.db import Repository

logger = logging.getLogger(__name__)


def create_app(provider=None, interval=None, db_path=None):
    seconds = float(interval if interval is not None else os.getenv("SAMPLE_INTERVAL_SECONDS", "5"))
    if not 1 <= seconds <= 3600:
        raise ValueError("Sampling interval must be between 1 and 3600 seconds")

    @asynccontextmanager
    async def lifespan(app):
        source = provider if provider is not None else SystemMetrics()
        app.state.repository = Repository(Path(db_path or os.getenv(
            "DATABASE_PATH", str(Path(__file__).resolve().parents[1] / "data/metrics.sqlite3")
        )))
        app.state.current = None
        app.state.sample_error = False

        def sample_once():
            try:
                sample = source.collect()
                app.state.repository.save(sample)
                app.state.current = sample
                app.state.sample_error = False
            except Exception:
                app.state.sample_error = True
                logger.exception("Metric collection or persistence failed; will retry")

        await asyncio.to_thread(sample_once)

        async def loop():
            while True:
                await asyncio.sleep(seconds)
                await asyncio.to_thread(sample_once)

        task = asyncio.create_task(loop())
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app = FastAPI(title="Jetson System Monitor", lifespan=lifespan)

    @app.get("/api/health")
    def health():
        sample = app.state.current
        stale = sample is None or (datetime.now(timezone.utc) - sample.timestamp).total_seconds() > seconds * 3
        return {"status": "degraded" if stale or app.state.sample_error else "ok",
                "sample_interval_seconds": seconds,
                "last_sample_at": sample.timestamp if sample else None}

    @app.get("/api/metrics/current", response_model=MetricSample)
    def current():
        if app.state.current is None:
            raise HTTPException(503, "No metric sample available yet")
        return app.state.current

    @app.get("/api/metrics/history", response_model=list[MetricSample])
    def history(start: datetime | None = Query(None, alias="from"),
                end: datetime | None = Query(None, alias="to"),
                limit: int = Query(720, ge=1, le=2000)):
        end = end or datetime.now(timezone.utc)
        start = start or end - timedelta(hours=1)
        if start.utcoffset() is None or end.utcoffset() is None:
            raise HTTPException(422, "History timestamps must include a timezone")
        if start > end:
            raise HTTPException(422, "from must be earlier than or equal to to")
        return app.state.repository.history(start, end, limit)

    return app


app = create_app()
