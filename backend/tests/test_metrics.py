from types import SimpleNamespace

import pytest

from app.metrics import SystemMetrics


@pytest.mark.parametrize("sensors, expected", [({}, None),
    ({"CPU-therm": [SimpleNamespace(current=48)]}, 48),
    ({"gpu": [SimpleNamespace(current=50)]}, None)])
def test_collection(monkeypatch, sensors, expected):
    monkeypatch.setattr("app.metrics.psutil.cpu_percent", lambda interval: 12)
    monkeypatch.setattr("app.metrics.psutil.virtual_memory", lambda: SimpleNamespace(percent=34))
    monkeypatch.setattr("app.metrics.psutil.disk_usage", lambda path: SimpleNamespace(percent=56))
    monkeypatch.setattr("app.metrics.psutil.boot_time", lambda: 100)
    monkeypatch.setattr("app.metrics.time.time", lambda: 200)
    monkeypatch.setattr("app.metrics.psutil.sensors_temperatures", lambda: sensors)
    result = SystemMetrics().collect()
    assert result.cpu_percent == 12
    assert result.memory_percent == 34
    assert result.disk_percent == 56
    assert result.uptime_seconds == 100
    assert result.temperature_c == expected


def test_sensor_os_error(monkeypatch):
    def fail():
        raise OSError("unsupported")
    monkeypatch.setattr("app.metrics.psutil.sensors_temperatures", fail)
    assert SystemMetrics().collect().temperature_c is None
