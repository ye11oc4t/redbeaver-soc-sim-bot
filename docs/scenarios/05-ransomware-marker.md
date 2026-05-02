# ransomware_marker

## Purpose

WORKDIR 내부에서만 파일 create/write/rename/delete를 발생시켜 FIM 탐지를 검증합니다.

## Required gates

```env
No active gate required
```

## Safety boundary

Only .redbeaver-work/ransomware_marker is modified.

## Run

```bash
python run.py --scenario ransomware_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
