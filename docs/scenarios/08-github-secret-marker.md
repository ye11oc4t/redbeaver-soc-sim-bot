# github_secret_marker

## Purpose

fake AKIA artifact와 optional AWS/Pacu read-only enumeration으로 secret exposure 대응을 검증합니다.

## Required gates

```env
ENABLE_AWS_READONLY=true
ENABLE_PACU=true
```

## Safety boundary

Fake key only. No real secret embedded.

## Run

```bash
python run.py --scenario github_secret_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
