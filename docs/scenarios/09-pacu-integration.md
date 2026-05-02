# Pacu integration

## Purpose

Pacu를 read-only allowlist wrapper로 실행합니다.

## Required gates

```env
ENABLE_PACU=true
```

## Safety boundary

Only allowlisted modules can run.

## Run

```bash
python run.py --scenario supply_chain_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
