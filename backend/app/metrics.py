import time
from datetime import datetime, timezone

import psutil

from app.models import MetricSample


class SystemMetrics:
    def collect(self) -> MetricSample:
        temperature = None
        try:
            for name, readings in psutil.sensors_temperatures().items():
                if "cpu" in name.lower() and readings:
                    temperature = readings[0].current
                    break
        except (AttributeError, OSError):
            pass

        # A short measurement window avoids psutil's initial nonblocking zero.
        cpu = psutil.cpu_percent(interval=0.1)
        return MetricSample(
            timestamp=datetime.now(timezone.utc),
            cpu_percent=cpu,
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage("/").percent,
            uptime_seconds=max(0, time.time() - psutil.boot_time()),
            temperature_c=temperature,
        )
