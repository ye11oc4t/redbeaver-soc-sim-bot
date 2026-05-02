from __future__ import annotations

import argparse
import importlib
import time
import traceback
from typing import Callable

from redbeaver.notify.discord import send_start, send_result, send_summary

BOTS = [
    ("ddos_marker", "Low-volume edge request marker for Cloudflare/CloudFront/WAF/ALB."),
    ("credential_stuffing_marker", "Fake login attempts for auth/rate-limit detection."),
    ("webshell_marker", "Harmless upload marker for upload/WAF visibility."),
    ("c2_marker", "Outbound HTTP/DNS beacon marker for EC2/NAT visibility."),
    ("ransomware_marker", "Local FIM marker inside WORKDIR only."),
    ("db_stealer_marker", "DB SELECT 1 + synthetic S3 marker, no dump."),
    ("supply_chain_marker", "Fake package + env-name inventory + optional AWS/Pacu read-only."),
    ("github_secret_marker", "Fake secret artifact + optional AWS/Pacu read-only."),
]

def list_scenarios() -> str:
    return "\n".join(f"- {name}: {desc}" for name, desc in BOTS)

def run_scenario(name: str, desc: str) -> dict:
    send_start(name, desc)
    start = time.time()
    ok = True
    output = ""
    try:
        mod = importlib.import_module(f"redbeaver.bots.{name}")
        output = mod.run()
    except Exception:
        ok = False
        output = traceback.format_exc()
    elapsed = time.time() - start
    send_result(name, ok, elapsed, output)
    return {"scenario": name, "ok": ok, "elapsed": elapsed, "output": output}

def cli() -> None:
    parser = argparse.ArgumentParser(description="redbeaver active-safe SOC validation bot")
    parser.add_argument("--list", action="store_true", help="List scenarios and exit")
    parser.add_argument("--scenario", default="all", help="Scenario name or 'all'")
    args = parser.parse_args()

    if args.list:
        print(list_scenarios())
        return

    selected = BOTS if args.scenario == "all" else [x for x in BOTS if x[0] == args.scenario]
    if not selected:
        raise SystemExit(f"Unknown scenario: {args.scenario}\n\nAvailable:\n{list_scenarios()}")

    results = []
    for name, desc in selected:
        print(f"[*] running {name}: {desc}")
        result = run_scenario(name, desc)
        results.append(result)
        print(result["output"])

    send_summary(results)
