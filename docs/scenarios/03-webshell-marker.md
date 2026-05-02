# webshell_marker

## Purpose

실행 불가능한 txt 파일 업로드로 upload/WAF/ALB 탐지를 검증합니다.

## Required gates

```env
ENABLE_NETWORK=true
ENABLE_UPLOAD_MARKER=true
```

## Safety boundary

Uploads redbeaver_webshell_marker.txt only. No PHP/RCE.

## Run

```bash
python run.py --scenario webshell_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
