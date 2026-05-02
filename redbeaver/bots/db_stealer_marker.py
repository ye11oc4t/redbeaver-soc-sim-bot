from __future__ import annotations

import json
import pymysql

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder
from redbeaver.utils.awsmark import s3_marker_put

NAME = "db_stealer_marker"
DESCRIPTION = "DB read-only marker: SELECT 1 only. Optional S3 marker PutObject to owned bucket."

def run() -> str:
    rec = EventRecorder(NAME)
    rec.add("scenario_start", safe=True, destructive=False, db_host=settings.db_host or "(unset)")

    synthetic = {
        "classification": "SIMULATED_DATA_ONLY",
        "rows": [{"id": i, "value": "dummy"} for i in range(5)],
        "note": "This is not a database dump.",
    }
    local_dump = settings.workdir / NAME / "synthetic_exfil_marker.json"
    local_dump.parent.mkdir(parents=True, exist_ok=True)
    local_dump.write_text(json.dumps(synthetic, indent=2), encoding="utf-8")
    rec.add("synthetic_dump_marker_created", path=str(local_dump), real_data=False)

    if settings.enable_db_readonly:
        if not all([settings.db_host, settings.db_user, settings.db_name]):
            rec.add("db_readonly_skipped", reason="DB_HOST/DB_USER/DB_NAME required")
        else:
            try:
                conn = pymysql.connect(
                    host=settings.db_host,
                    port=settings.db_port,
                    user=settings.db_user,
                    password=settings.db_password,
                    database=settings.db_name,
                    connect_timeout=5,
                    read_timeout=5,
                    write_timeout=5,
                    cursorclass=pymysql.cursors.DictCursor,
                )
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 AS redbeaver_marker")
                    row = cur.fetchone()
                conn.close()
                rec.add("db_select_one_marker", result=row)
            except Exception as e:
                rec.add("db_readonly_error", error=str(e))

    if settings.enable_aws_readonly and settings.enable_s3_marker:
        try:
            result = s3_marker_put(NAME, rec.trace_id, synthetic)
            rec.add("s3_marker_put", **result)
        except Exception as e:
            rec.add("s3_marker_error", error=str(e))

    path = rec.save()
    return f"{NAME}: synthetic_marker={local_dump}; events={path}"
