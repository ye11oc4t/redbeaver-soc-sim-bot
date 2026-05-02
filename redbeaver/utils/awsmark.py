from __future__ import annotations

from datetime import datetime, timezone
import json
import boto3

from redbeaver.config import settings

def readonly_identity_marker() -> dict:
    session = boto3.Session()
    out = {}
    sts = session.client("sts")
    out["identity"] = sts.get_caller_identity()

    try:
        iam = session.client("iam")
        out["account_aliases"] = iam.list_account_aliases().get("AccountAliases", [])
    except Exception as e:
        out["account_aliases_error"] = str(e)

    return out

def s3_marker_put(scenario: str, trace_id: str, payload: dict) -> dict:
    if not settings.marker_bucket:
        return {"skipped": True, "reason": "MARKER_BUCKET is empty"}
    session = boto3.Session()
    s3 = session.client("s3")
    key = f"{settings.marker_prefix}/{scenario}/{trace_id}.json"
    body = json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": settings.run_id,
        "scenario": scenario,
        "trace_id": trace_id,
        "payload": payload,
    }, indent=2, ensure_ascii=False, default=str).encode()
    s3.put_object(
        Bucket=settings.marker_bucket,
        Key=key,
        Body=body,
        ContentType="application/json",
        Metadata={
            "redbeaver-scenario": scenario,
            "redbeaver-run-id": settings.run_id,
            "redbeaver-trace-id": trace_id,
        },
    )
    return {"bucket": settings.marker_bucket, "key": key}
