# ddos_marker

## Purpose

외부 runner에서 낮은 요청 burst를 만들어 Cloudflare/CloudFront/WAF/ALB 관측을 검증합니다.

## Required gates

```env
ENABLE_NETWORK=true
```

## Safety boundary

HTTP GET marker headers. Hard cap: 50 requests / concurrency 5.

## Run

```bash
python run.py --scenario ddos_marker
```

## Expected SOC visibility

- `X-Redbeaver-Scenario`
- `X-Redbeaver-Run-Id`
- `X-Redbeaver-Trace-Id`
- `results/*.json`
- Discord start/done/summary if webhook is configured
