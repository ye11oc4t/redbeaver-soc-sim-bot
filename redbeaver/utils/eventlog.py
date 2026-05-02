from __future__ import annotations

import json
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from redbeaver.config import settings

class EventRecorder:
    def __init__(self, scenario: str):
        self.scenario = scenario
        self.events: list[dict[str, Any]] = []
        self.trace_id = str(uuid.uuid4())[:12]

    def add(self, event: str, **fields: Any) -> None:
        self.events.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": settings.run_id,
            "trace_id": self.trace_id,
            "scenario": self.scenario,
            "execution_zone": settings.execution_zone,
            "host": socket.gethostname(),
            "event": event,
            **fields,
        })

    def save(self) -> Path:
        out = settings.results_dir / f"{self.scenario}-{self.trace_id}.json"
        out.write_text(json.dumps(self.events, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        return out

def marker_headers(scenario: str, trace_id: str) -> dict[str, str]:
    return {
        "User-Agent": f"redbeaver-soc-marker/{scenario}",
        "X-Redbeaver-Scenario": scenario,
        "X-Redbeaver-Run-Id": settings.run_id,
        "X-Redbeaver-Trace-Id": trace_id,
        "X-Redbeaver-Mode": "active-safe",
    }
