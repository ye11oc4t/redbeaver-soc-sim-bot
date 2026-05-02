from __future__ import annotations

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder
from redbeaver.utils.awsmark import readonly_identity_marker
from redbeaver.utils.pacu import run_allowlisted_pacu_modules

NAME = "github_secret_marker"
DESCRIPTION = "Fake leaked-secret artifact + optional STS/Pacu read-only marker. No real secret is embedded."

FAKE_KEY = "AKIAIOSFODNN7EXAMPLE"
FAKE_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False)

    leak_dir = settings.workdir / NAME
    leak_dir.mkdir(parents=True, exist_ok=True)
    fake_env = leak_dir / ".env.leaked.example"
    fake_env.write_text(
        f"AWS_ACCESS_KEY_ID={FAKE_KEY}\nAWS_SECRET_ACCESS_KEY={FAKE_SECRET}\n",
        encoding="utf-8",
    )
    rec.add("fake_secret_artifact_created", path=str(fake_env), real_secret=False, pattern="AKIA-like example key")

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
        rec.add("pacu_mapping_note", modules=["aws__enum_account", "iam__enum_permissions", "ec2__enum"], executed=False)

    path = rec.save()
    return f"{NAME}: fake_secret={fake_env}; optional read-only Pacu processed={settings.enable_pacu}; events={path}"
