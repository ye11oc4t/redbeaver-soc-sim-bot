from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from redbeaver.config import settings

PACU_READONLY_ALLOWLIST = {
    "aws__enum_account",
    "iam__enum_permissions",
    "iam__enum_users_roles_policies_groups",
    "ec2__enum",
    "rds__enum",
    "lambda__enum",
    "cloudtrail__enum",
    "guardduty__list_findings",
}

@dataclass
class PacuResult:
    module: str
    ok: bool
    returncode: int
    stdout: str
    stderr: str

def validate_modules(modules: list[str]) -> None:
    denied = [m for m in modules if m not in PACU_READONLY_ALLOWLIST]
    if denied:
        raise ValueError(
            "Denied Pacu module(s): "
            + ", ".join(denied)
            + ". Only read-only enumeration modules are allowed by redbeaver."
        )

def pacu_available() -> bool:
    return shutil.which(settings.pacu_binary) is not None

def run_allowlisted_pacu_modules(modules: list[str]) -> list[PacuResult]:
    validate_modules(modules)
    if not pacu_available():
        return [PacuResult(
            module="__pacu_binary__",
            ok=False,
            returncode=127,
            stdout="",
            stderr=f"Pacu binary not found: {settings.pacu_binary}",
        )]

    results: list[PacuResult] = []
    for module in modules:
        cmd = [
            settings.pacu_binary,
            "--session",
            settings.pacu_session_name,
            "--exec",
            f"run {module}",
        ]
        try:
            p = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=settings.pacu_timeout_seconds,
            )
            results.append(PacuResult(
                module=module,
                ok=p.returncode == 0,
                returncode=p.returncode,
                stdout=p.stdout[-2000:],
                stderr=p.stderr[-2000:],
            ))
        except subprocess.TimeoutExpired as e:
            results.append(PacuResult(
                module=module,
                ok=False,
                returncode=124,
                stdout=(e.stdout or "")[-2000:] if isinstance(e.stdout, str) else "",
                stderr="Pacu module timed out",
            ))
    return results
