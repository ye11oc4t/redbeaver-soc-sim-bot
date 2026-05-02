from __future__ import annotations

from urllib.parse import urljoin
import requests

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder, marker_headers

NAME = "webshell_marker"
DESCRIPTION = "Harmless upload marker for upload/WAF/ALB visibility. No executable webshell."

MARKER_CONTENT = b"REDBEAVER WEBSHELL MARKER - hello world only, not executable\n"

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False, upload_endpoint=settings.upload_endpoint)

    if settings.enable_network and settings.enable_upload_marker:
        url = urljoin(settings.target_base_url + "/", settings.upload_endpoint.lstrip("/"))
        try:
            r = requests.post(
                url,
                headers=marker_headers(NAME, rec.trace_id),
                files={"file": ("redbeaver_webshell_marker.txt", MARKER_CONTENT, "text/plain")},
                data={"redbeaver_marker": "true", "scenario": NAME},
                timeout=settings.http_timeout,
                verify=False,
            )
            rec.add("upload_marker_sent", status_code=r.status_code, filename="redbeaver_webshell_marker.txt")
        except Exception as e:
            rec.add("upload_marker_error", error=str(e))
    else:
        rec.add("dry_run_upload_marker", filename="redbeaver_webshell_marker.txt")

    path = rec.save()
    return f"{NAME}: completed; events={path}"
