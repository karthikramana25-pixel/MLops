"""Prometheus metrics for HTTP requests handled by the API."""

from time import perf_counter
from typing import Any

from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "http_requests",
    "HTTP requests handled by the API, excluding metrics scrapes.",
    ("method", "route", "status_code"),
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


class PrometheusMetricsMiddleware:
    """Measure HTTP requests with bounded-cardinality route labels."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope.get("path", "").startswith("/metrics"):
            await self.app(scope, receive, send)
            return

        start_time = perf_counter()
        status_code = 500

        async def send_and_capture_status(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_and_capture_status)
        finally:
            method = scope.get("method", "unknown")
            route = getattr(scope.get("route"), "path", "unmatched")
            HTTP_REQUESTS.labels(method, route, str(status_code)).inc()
            HTTP_REQUEST_DURATION.labels(method, route).observe(perf_counter() - start_time)
