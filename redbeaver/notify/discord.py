from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import requests

from redbeaver.config import settings

COLOR = {
    "start": 0x3b82f6,
    "done": 0x22c55e,
    "error": 0xef4444,
    "summary": 0x8b5cf6,
}

def enabled() -> bool:
    return bool(settings.discord_webhook_url)

def _post(embed: dict[str, Any]) -> None:
    if not enabled():
        return
    payload = {"embeds": [embed]}
    r = requests.post(settings.discord_webhook_url, json=payload, timeout=8)
    r.raise_for_status()

def send_start(name: str, description: str) -> None:
    _post({
        "title": f"[redbeaver] {name} start",
        "description": description,
        "color": COLOR["start"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": [
            {"name": "run_id", "value": settings.run_id, "inline": True},
            {"name": "zone", "value": settings.execution_zone, "inline": True},
            {"name": "mode", "value": "active-safe", "inline": True},
        ],
    })

def send_result(name: str, ok: bool, elapsed: float, output: str) -> None:
    trimmed = output[:950] if output else "(no output)"
    _post({
        "title": f"[redbeaver] {name} {'done' if ok else 'error'}",
        "color": COLOR["done"] if ok else COLOR["error"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": [
            {"name": "status", "value": "completed" if ok else "error", "inline": True},
            {"name": "elapsed", "value": f"{elapsed:.2f}s", "inline": True},
            {"name": "output", "value": f"```{trimmed}```", "inline": False},
        ],
    })

def send_summary(results: list[dict[str, Any]]) -> None:
    lines = []
    for r in results:
        icon = "OK" if r.get("ok") else "ERR"
        lines.append(f"{icon} {r['scenario']} - {r['elapsed']:.2f}s")
    _post({
        "title": "[redbeaver] run summary",
        "description": "\n".join(lines)[:3500],
        "color": COLOR["summary"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": [
            {"name": "total", "value": str(len(results)), "inline": True},
            {"name": "completed", "value": str(sum(1 for r in results if r.get("ok"))), "inline": True},
            {"name": "errors", "value": str(sum(1 for r in results if not r.get("ok"))), "inline": True},
        ],
    })
