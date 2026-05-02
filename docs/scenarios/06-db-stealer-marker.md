# db_stealer_marker

## Purpose

DB SELECT 1과 synthetic S3 marker로 RDS/S3/CloudTrail 관측을 검증합니다.

## Required gates

```env
ENABLE_DB_READONLY=true
ENABLE_AWS_READONLY=true
ENABLE_S3_MARKER=true
```

## Safety boundary

No table dump. SELECT 1 only.

## Run

```bash
python run.py --scenario db_stealer_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
