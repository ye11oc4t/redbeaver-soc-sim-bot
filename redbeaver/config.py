from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

def _int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw not in (None, "") else default
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value

def _list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

@dataclass(frozen=True)
class Settings:
    run_id: str = os.getenv("REDBEAVER_RUN_ID", "local-run")
    execution_zone: str = os.getenv("EXECUTION_ZONE", "external")

    results_dir: Path = Path(os.getenv("RESULTS_DIR", "results"))
    workdir: Path = Path(os.getenv("WORKDIR", ".redbeaver-work"))

    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")

    enable_network: bool = _bool("ENABLE_NETWORK", False)
    enable_aws_readonly: bool = _bool("ENABLE_AWS_READONLY", False)
    enable_s3_marker: bool = _bool("ENABLE_S3_MARKER", False)
    enable_db_readonly: bool = _bool("ENABLE_DB_READONLY", False)
    enable_upload_marker: bool = _bool("ENABLE_UPLOAD_MARKER", False)
    enable_auth_marker: bool = _bool("ENABLE_AUTH_MARKER", False)
    enable_pacu: bool = _bool("ENABLE_PACU", False)

    target_base_url: str = os.getenv("TARGET_BASE_URL", "https://example.invalid").rstrip("/")
    target_endpoints: list[str] = None

    upload_endpoint: str = os.getenv("UPLOAD_ENDPOINT", "/api/upload")
    login_endpoint: str = os.getenv("LOGIN_ENDPOINT", "/api/login")

    # Hard caps prevent this from becoming a load generator.
    http_total_requests: int = _int("HTTP_TOTAL_REQUESTS", 20, minimum=1, maximum=50)
    http_concurrency: int = _int("HTTP_CONCURRENCY", 3, minimum=1, maximum=5)
    http_timeout: int = _int("HTTP_TIMEOUT", 4, minimum=1, maximum=10)
    auth_max_attempts: int = _int("AUTH_MAX_ATTEMPTS", 12, minimum=1, maximum=30)

    c2_collector_url: str = os.getenv("C2_COLLECTOR_URL", "http://127.0.0.1:8080/beacon")
    c2_domain: str = os.getenv("C2_DOMAIN", "example.invalid")
    c2_beacons: int = _int("C2_BEACONS", 5, minimum=1, maximum=10)
    c2_interval_seconds: int = _int("C2_INTERVAL_SECONDS", 5, minimum=1, maximum=30)

    db_host: str = os.getenv("DB_HOST", "")
    db_port: int = _int("DB_PORT", 3306, minimum=1, maximum=65535)
    db_user: str = os.getenv("DB_USER", "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "")

    marker_bucket: str = os.getenv("MARKER_BUCKET", "")
    marker_prefix: str = os.getenv("MARKER_PREFIX", "redbeaver/markers").strip("/")

    pacu_binary: str = os.getenv("PACU_BINARY", "pacu")
    pacu_session_name: str = os.getenv("PACU_SESSION_NAME", "redbeaver-safe")
    pacu_modules: list[str] = None
    pacu_timeout_seconds: int = _int("PACU_TIMEOUT_SECONDS", 180, minimum=10, maximum=600)

    def __post_init__(self):
        object.__setattr__(self, "target_endpoints", _list("TARGET_ENDPOINTS", "/,/health,/api/products,/api/login,/api/orders,/admin"))
        object.__setattr__(self, "pacu_modules", _list("PACU_MODULES", "aws__enum_account,iam__enum_permissions,ec2__enum"))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.workdir.mkdir(parents=True, exist_ok=True)

settings = Settings()
