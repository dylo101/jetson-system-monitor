import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from app.metrics import SystemMetrics
from app.models import MetricSample

logger = logging.getLogger(__name__)


def create_app(provider=None, interval=None):
    seconds = float(interval if interval is not None else os.getenv("SAMPLE_INTERVAL_SECONDS", "5"))
    if not 1 <= seconds <= 3600:
        raise ValueError("Sampling interval must be between 1 and 3600 seconds")

    @asynccontextmanager
    async def lifespan(app):
        source = provider if provider is not None else SystemMetrics()
        app.state.current = None
        app.state.sample_error = False

        def sample_once():
            try:
                app.state.current = source.collect()
                app.state.sample_error = False
            except Exception:
                app.state.sample_error = True
                logger.exception("Metric collection failed; will retry")

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

    return app


app = create_app()
