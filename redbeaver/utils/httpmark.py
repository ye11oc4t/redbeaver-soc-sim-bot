from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import random
import requests

from redbeaver.config import settings
from redbeaver.utils.eventlog import marker_headers

def request_marker_burst(scenario: str, trace_id: str, method: str = "GET", path_pool: list[str] | None = None, body: dict | None = None) -> dict:
    paths = path_pool or settings.target_endpoints
    total = settings.http_total_requests
    concurrency = settings.http_concurrency

    def one(i: int) -> tuple[int, str]:
        path = random.choice(paths)
        url = urljoin(settings.target_base_url + "/", path.lstrip("/"))
        headers = marker_headers(scenario, trace_id)
        try:
            if method.upper() == "POST":
                r = requests.post(url, headers=headers, json=body or {"redbeaver": "marker", "i": i}, timeout=settings.http_timeout, verify=False)
            else:
                r = requests.get(url, headers=headers, timeout=settings.http_timeout, verify=False)
            return r.status_code, url
        except Exception:
            return 0, url

    counts = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "err": 0}
    urls = set()
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(one, i) for i in range(total)]
        for f in as_completed(futures):
            code, url = f.result()
            urls.add(url)
            if 200 <= code < 300: counts["2xx"] += 1
            elif 300 <= code < 400: counts["3xx"] += 1
            elif 400 <= code < 500: counts["4xx"] += 1
            elif 500 <= code < 600: counts["5xx"] += 1
            else: counts["err"] += 1
    return {"total": total, "concurrency": concurrency, "counts": counts, "sample_urls": sorted(urls)[:5]}
