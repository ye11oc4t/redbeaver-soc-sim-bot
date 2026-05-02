# credential_stuffing_marker

## Purpose

가짜 계정으로 소량 로그인 실패 이벤트를 만들어 auth/rate-limit 탐지를 검증합니다.

## Required gates

```env
ENABLE_NETWORK=true
ENABLE_AUTH_MARKER=true
```

## Safety boundary

Fake users only. Hard cap: 30 attempts.

## Run

```bash
python run.py --scenario credential_stuffing_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
