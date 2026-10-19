from datetime import datetime, timedelta, timezone

from app.db import Repository, utc_text
from app.models import MetricSample


def sample(at):
    return MetricSample(timestamp=at, cpu_percent=20, memory_percent=40,
                        disk_percent=60, uptime_seconds=100)


def test_persistence_order_bounds_and_retention(tmp_path):
    path = tmp_path / "metrics.db"
    repo = Repository(path)
    now = datetime.now(timezone.utc)
    repo.save(sample(now - timedelta(days=2)))
    for seconds in [30, 10, 20]:
        repo.save(sample(now - timedelta(seconds=seconds)))
    restarted = Repository(path)
    rows = restarted.history(now - timedelta(days=3), now, 100)
    assert [row.timestamp for row in rows] == [now - timedelta(seconds=s) for s in [30, 20, 10]]
    assert len(restarted.history(now - timedelta(seconds=20), now, 100)) == 2
    assert restarted.history(now - timedelta(days=3), now, 1)[0] == rows[-1]
    assert restarted.history(now + timedelta(seconds=1), now + timedelta(seconds=2), 100) == []


def test_row_cap(tmp_path):
    repo = Repository(tmp_path / "metrics.db")
    now = datetime.now(timezone.utc)
    with repo.connect() as db:
        db.executemany("INSERT INTO metric_samples VALUES (?, 1, 1, 1, 1, NULL)",
                       [(utc_text(now - timedelta(milliseconds=i + 1)),) for i in range(20001)])
    repo.save(sample(now))
    with repo.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM metric_samples").fetchone()[0] == 20000
