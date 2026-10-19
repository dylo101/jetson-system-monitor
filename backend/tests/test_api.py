from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app
from app.models import MetricSample


class FakeProvider:
    def collect(self):
        return MetricSample(timestamp=datetime.now(timezone.utc), cpu_percent=20,
                            memory_percent=40, disk_percent=60, uptime_seconds=100)


def test_current_and_health(tmp_path):
    with TestClient(create_app(FakeProvider(), interval=3600, db_path=tmp_path / "test.db")) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        response = client.get("/api/metrics/current")
        assert response.status_code == 200
        assert response.json()["cpu_percent"] == 20
        assert response.json()["temperature_c"] is None


def test_collection_failure(tmp_path):
    class BrokenProvider:
        def collect(self):
            raise OSError("unavailable")
    with TestClient(create_app(BrokenProvider(), interval=3600, db_path=tmp_path / "test.db")) as client:
        assert client.get("/api/health").json()["status"] == "degraded"
        assert client.get("/api/metrics/current").status_code == 503
        assert client.get("/api/metrics/history").json() == []


def test_history_validation_and_restart(tmp_path):
    path = tmp_path / "test.db"
    with TestClient(create_app(FakeProvider(), interval=3600, db_path=path)) as client:
        first = client.get("/api/metrics/current").json()
        assert client.get("/api/metrics/history").json() == [first]
        for params in ({"limit": 0}, {"limit": 2001}, {"from": "bad"},
                       {"from": "2026-01-01T00:00:00"},
                       {"from": "2026-01-02T00:00:00Z", "to": "2026-01-01T00:00:00Z"}):
            assert client.get("/api/metrics/history", params=params).status_code == 422
    with TestClient(create_app(FakeProvider(), interval=3600, db_path=path)) as client:
        rows = client.get("/api/metrics/history").json()
        assert len(rows) == 2
        assert rows[0] == first
