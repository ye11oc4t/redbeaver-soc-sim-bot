# c2_marker

## Purpose

private EC2에서 외부 collector/DNS로 beacon marker를 보내 NAT/egress 탐지를 검증합니다.

## Required gates

```env
ENABLE_NETWORK=true
```

## Safety boundary

HTTP POST + DNS query marker. No command execution.

## Run

```bash
python run.py --scenario c2_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
