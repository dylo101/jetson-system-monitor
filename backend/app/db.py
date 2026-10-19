import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models import MetricSample


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


class Repository:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS metric_samples (
                timestamp TEXT PRIMARY KEY,
                cpu_percent REAL NOT NULL, memory_percent REAL NOT NULL,
                disk_percent REAL NOT NULL, uptime_seconds REAL NOT NULL,
                temperature_c REAL
            )""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def save(self, sample: MetricSample):
        cutoff = utc_text(datetime.now(timezone.utc) - timedelta(hours=24))
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO metric_samples VALUES (?, ?, ?, ?, ?, ?)",
                       (utc_text(sample.timestamp), sample.cpu_percent, sample.memory_percent,
                        sample.disk_percent, sample.uptime_seconds, sample.temperature_c))
            db.execute("DELETE FROM metric_samples WHERE timestamp < ?", (cutoff,))
            db.execute("""DELETE FROM metric_samples WHERE timestamp NOT IN
                (SELECT timestamp FROM metric_samples ORDER BY timestamp DESC LIMIT 20000)""")

    def history(self, start: datetime, end: datetime, limit: int):
        with self.connect() as db:
            rows = db.execute("""SELECT * FROM metric_samples
                WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC LIMIT ?""",
                (utc_text(start), utc_text(end), limit)).fetchall()
        return [MetricSample(**dict(row)) for row in reversed(rows)]
