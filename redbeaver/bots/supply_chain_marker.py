from __future__ import annotations

import json
import os

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder
from redbeaver.utils.awsmark import readonly_identity_marker
from redbeaver.utils.pacu import run_allowlisted_pacu_modules

NAME = "supply_chain_marker"
DESCRIPTION = "Supply-chain style marker: fake package artifact + env-name inventory + optional AWS/Pacu read-only enumeration."

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False)

    pkg_dir = settings.workdir / NAME / "fake_npm_package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    pkg = {
        "name": "redbeaver-supply-chain-marker",
        "version": "0.0.1",
        "description": "Harmless postinstall marker for SOC validation",
        "scripts": {"postinstall": "echo REDBEAVER_SUPPLY_CHAIN_MARKER"},
    }
    (pkg_dir / "package.json").write_text(json.dumps(pkg, indent=2), encoding="utf-8")
    rec.add("fake_package_artifact_created", path=str(pkg_dir / "package.json"), postinstall_executes_only_echo=True)

    env_names = [k for k in os.environ.keys() if any(token in k.upper() for token in ["AWS", "TOKEN", "SECRET", "KEY"])]
    rec.add("environment_name_inventory", names=sorted(env_names), values_collected=False)

    if settings.enable_aws_readonly:
        try:
            ident = readonly_identity_marker()
            rec.add("aws_readonly_identity_marker", identity=ident)
        except Exception as e:
            rec.add("aws_readonly_error", error=str(e))

    if settings.enable_pacu:
        try:
            results = run_allowlisted_pacu_modules(settings.pacu_modules)
            for item in results:
                rec.add("pacu_module_result", module=item.module, ok=item.ok, returncode=item.returncode, stdout_tail=item.stdout[-900:], stderr_tail=item.stderr[-900:])
        except Exception as e:
            rec.add("pacu_wrapper_error", error=str(e))
    else:
        rec.add("pacu_mapping_note", modules=settings.pacu_modules, executed=False)

    path = rec.save()
    return f"{NAME}: fake_package={pkg_dir}; pacu_enabled={settings.enable_pacu}; events={path}"
