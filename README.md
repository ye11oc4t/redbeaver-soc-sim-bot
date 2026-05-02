# redbeaver — Active-Safe SOC Validation Bot

`redbeaver`는 Blue Team/SOC 구축 검증을 위한 **active-safe marker bot**입니다.

목표는 실제 침투·탈취·파괴가 아니라, 공격 시나리오와 유사한 **관측 가능한 흔적**을 안전하게 남겨서 다음 파이프라인을 검증하는 것입니다.

- Cloudflare / CloudFront / WAF / ALB 로그
- EC2 egress / NAT instance / DNS / HTTP beacon 로그
- RDS 접속 로그
- S3 PutObject / CloudTrail
- AWS STS/IAM/EC2 read-only enumeration
- Discord 실행 알림
- Wazuh, TheHive, Security Hub, CloudWatch 기반 룰 튜닝용 이벤트

## Safety Model

기본값은 전부 비활성화입니다.

```env
ENABLE_NETWORK=false
ENABLE_AWS_READONLY=false
ENABLE_S3_MARKER=false
ENABLE_DB_READONLY=false
ENABLE_UPLOAD_MARKER=false
ENABLE_AUTH_MARKER=false
ENABLE_PACU=false
```

따라서 기본 실행은 로컬 JSON 이벤트와 워크디렉터리 내부 마커만 생성합니다.

이 프로젝트는 다음을 수행하지 않습니다.

- 실제 DDoS
- 실제 웹쉘 업로드/RCE
- 실제 credential stuffing
- 실제 DB dump/exfiltration
- Pacu privesc/backdoor/persistence/destructive module
- CloudTrail 비활성화
- S3 데이터 다운로드/탈취
- 운영 파일 암호화/삭제

## Architecture Placement

시나리오마다 실행 위치가 다릅니다.

| Scenario | Recommended runner | Expected visibility |
|---|---|---|
| `ddos_marker` | external runner | Cloudflare → CloudFront → WAF → ALB |
| `credential_stuffing_marker` | external runner | Cloudflare/WAF/ALB/auth API logs |
| `webshell_marker` | external runner | WAF/ALB/upload endpoint logs |
| `c2_marker` | private app EC2 | EC2 egress → NAT → external collector/DNS |
| `ransomware_marker` | monitored app EC2 | FIM/Velociraptor/Wazuh file events |
| `db_stealer_marker` | app EC2 with RDS access | RDS connect/select logs, optional S3/CloudTrail |
| `supply_chain_marker` | DevOps runner/bastion | STS/IAM/EC2 read-only CloudTrail, optional Pacu |
| `github_secret_marker` | DevOps runner/bastion | fake AKIA artifact, STS, optional Pacu |

## Install

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

## List Scenarios

```bash
python run.py --list
```

## Run All in Default Safe Mode

```bash
python run.py --scenario all
```

## Discord Notification

Set this in `.env`.

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Then every scenario emits:

- scenario start
- scenario done/error
- run summary

## External Edge/WAF Test

```env
ENABLE_NETWORK=true
TARGET_BASE_URL=https://your-service.example.com
HTTP_TOTAL_REQUESTS=20
HTTP_CONCURRENCY=3
```

```bash
python run.py --scenario ddos_marker
python run.py --scenario credential_stuffing_marker
python run.py --scenario webshell_marker
```

For auth/upload marker, explicitly enable the gates:

```env
ENABLE_AUTH_MARKER=true
ENABLE_UPLOAD_MARKER=true
LOGIN_ENDPOINT=/api/login
UPLOAD_ENDPOINT=/api/upload
```

## Private EC2 Egress Test

Run this on an app EC2 behind NAT.

```env
ENABLE_NETWORK=true
EXECUTION_ZONE=app-ec2
C2_COLLECTOR_URL=http://your-owned-collector.example.com:8080/beacon
C2_DOMAIN=c2-test.yourdomain.example
```

```bash
python run.py --scenario c2_marker
```

## RDS/S3 Marker Test

Run this on an app EC2 allowed to reach RDS.

```env
ENABLE_DB_READONLY=true
ENABLE_AWS_READONLY=true
ENABLE_S3_MARKER=true

DB_HOST=your-rds.endpoint.ap-northeast-2.rds.amazonaws.com
DB_PORT=3306
DB_USER=readonly_user
DB_PASSWORD=...
DB_NAME=appdb

MARKER_BUCKET=your-owned-marker-bucket
MARKER_PREFIX=redbeaver/markers
```

```bash
python run.py --scenario db_stealer_marker
```

The DB query is only:

```sql
SELECT 1 AS redbeaver_marker;
```

No table dump is performed.

## Pacu Integration

Pacu is optional and read-only allowlisted.

```env
ENABLE_AWS_READONLY=true
ENABLE_PACU=true
PACU_BINARY=pacu
PACU_SESSION_NAME=redbeaver-safe
PACU_MODULES=aws__enum_account,iam__enum_permissions,ec2__enum
```

Allowed modules:

```text
aws__enum_account
iam__enum_permissions
iam__enum_users_roles_policies_groups
ec2__enum
rds__enum
lambda__enum
cloudtrail__enum
guardduty__list_findings
```

Denied by design:

```text
privesc
backdoor
persistence
cloudtrail disable
s3 download
exfiltration
destructive module
```

Run:

```bash
python run.py --scenario supply_chain_marker
python run.py --scenario github_secret_marker
```

## Output

All scenario events are saved under:

```text
results/*.json
```

Each event includes:

```json
{
  "run_id": "local-run",
  "trace_id": "...",
  "scenario": "...",
  "execution_zone": "...",
  "event": "..."
}
```

HTTP markers include headers:

```text
X-Redbeaver-Scenario
X-Redbeaver-Run-Id
X-Redbeaver-Trace-Id
X-Redbeaver-Mode: active-safe
```

Use these fields for WAF/ALB/Wazuh/CloudWatch filtering.
