from __future__ import annotations

from urllib.parse import urljoin
import requests

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder, marker_headers

NAME = "credential_stuffing_marker"
DESCRIPTION = "Small fake-login marker for auth failure/rate-limit detection. No real credentials."

FAKE_USERS = ["rb_admin", "rb_operator", "rb_guest", "rb_test"]
FAKE_PASSWORDS = ["WrongPassword123!", "Spring2026!", "RedbeaverMarker!", "NotARealPassword!"]

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False, login_endpoint=settings.login_endpoint)

    attempts = []
    for u in FAKE_USERS:
        for p in FAKE_PASSWORDS:
            if len(attempts) >= settings.auth_max_attempts:
                break
            attempts.append((u, p))

    if settings.enable_network and settings.enable_auth_marker:
        url = urljoin(settings.target_base_url + "/", settings.login_endpoint.lstrip("/"))
        for i, (username, password) in enumerate(attempts):
            try:
                r = requests.post(
                    url,
                    headers=marker_headers(NAME, rec.trace_id),
                    json={
                        "username": username,
                        "password": password,
                        "redbeaver_marker": True,
                    },
                    timeout=settings.http_timeout,
                    verify=False,
                )
                rec.add("fake_login_attempt", index=i, username=username, status_code=r.status_code)
            except Exception as e:
                rec.add("fake_login_attempt_error", index=i, username=username, error=str(e))
    else:
        for i, (username, _) in enumerate(attempts):
            rec.add("dry_run_login_attempt", index=i, username=username)

    path = rec.save()
    return f"{NAME}: attempts={len(attempts)}; events={path}"
