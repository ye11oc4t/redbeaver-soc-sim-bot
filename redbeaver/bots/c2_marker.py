from __future__ import annotations

import base64
import socket
import time
import requests

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder, marker_headers

NAME = "c2_marker"
DESCRIPTION = "Outbound HTTP/DNS beacon marker for EC2-to-NAT egress visibility. No command execution."

def _dns_marker(qname: str) -> str:
    try:
        socket.getaddrinfo(qname, None)
        return "resolved_or_queried"
    except Exception as e:
        return f"query_attempted:{type(e).__name__}"

def run() -> str:
    rec = EventRecorder(NAME)
    host_id = base64.urlsafe_b64encode(socket.gethostname().encode()).decode().rstrip("=")[:24]
    rec.add("scenario_start", safe=True, destructive=False, collector=settings.c2_collector_url, domain=settings.c2_domain)

    for i in range(settings.c2_beacons):
        payload = {
            "redbeaver_marker": True,
            "scenario": NAME,
            "run_id": settings.run_id,
            "trace_id": rec.trace_id,
            "seq": i,
            "host_id": host_id,
            "message": "hello-world-c2-marker",
        }

        if settings.enable_network:
            try:
                r = requests.post(
                    settings.c2_collector_url,
                    headers=marker_headers(NAME, rec.trace_id),
                    json=payload,
                    timeout=settings.http_timeout,
                )
                rec.add("http_beacon_sent", seq=i, status_code=r.status_code)
            except Exception as e:
                rec.add("http_beacon_error", seq=i, error=str(e))

            qname = f"{host_id.lower()}.{i}.{settings.c2_domain}"
            dns_result = _dns_marker(qname)
            rec.add("dns_beacon_marker", seq=i, qname=qname, result=dns_result)
        else:
            rec.add("dry_run_beacon", seq=i, collector=settings.c2_collector_url)

        if i + 1 < settings.c2_beacons:
            time.sleep(settings.c2_interval_seconds)

    path = rec.save()
    return f"{NAME}: beacons={settings.c2_beacons}; events={path}"
