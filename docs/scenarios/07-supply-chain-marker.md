# supply_chain_marker

## Purpose

fake package artifact와 optional AWS/Pacu read-only enumeration으로 공급망/IAM 정찰 탐지를 검증합니다.

## Required gates

```env
ENABLE_AWS_READONLY=true
ENABLE_PACU=true
```

## Safety boundary

No malicious postinstall. Env values are not collected.

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
