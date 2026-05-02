from __future__ import annotations

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder
from redbeaver.utils.httpmark import request_marker_burst

NAME = "ddos_marker"
DESCRIPTION = "Low-volume edge request burst marker for Cloudflare/CloudFront/WAF/ALB visibility."

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False, target=settings.target_base_url)

    if settings.enable_network:
        result = request_marker_burst(NAME, rec.trace_id, method="GET")
        rec.add("network_marker_burst", **result)
    else:
        for i in range(settings.http_total_requests):
            rec.add("dry_run_request_marker", index=i, target=settings.target_base_url)

    path = rec.save()
    return f"{NAME}: completed; events={path}"
