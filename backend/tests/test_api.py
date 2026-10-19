from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app
from app.models import MetricSample


class FakeProvider:
    def collect(self):
        return MetricSample(timestamp=datetime.now(timezone.utc), cpu_percent=20,
                            memory_percent=40, disk_percent=60, uptime_seconds=100)


def test_current_and_health():
    with TestClient(create_app(FakeProvider(), interval=3600)) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        response = client.get("/api/metrics/current")
        assert response.status_code == 200
        assert response.json()["cpu_percent"] == 20
        assert response.json()["temperature_c"] is None


def test_collection_failure():
    class BrokenProvider:
        def collect(self):
            raise OSError("unavailable")
    with TestClient(create_app(BrokenProvider(), interval=3600)) as client:
        assert client.get("/api/health").json()["status"] == "degraded"
        assert client.get("/api/metrics/current").status_code == 503
