# Safety Notes

`redbeaver`는 공격 도구가 아니라 SOC 검증용 marker generator입니다.

## Default deny

All active actions are disabled by default.

```env
ENABLE_NETWORK=false
ENABLE_AWS_READONLY=false
ENABLE_S3_MARKER=false
ENABLE_DB_READONLY=false
ENABLE_UPLOAD_MARKER=false
ENABLE_AUTH_MARKER=false
ENABLE_PACU=false
```

## No destructive behavior

The project does not encrypt operational files, delete production data, execute remote shell commands, brute-force real accounts, or exfiltrate data.

## Local file marker scope

`ransomware_marker` only modifies files inside `WORKDIR/ransomware_marker`.

## Database behavior

`db_stealer_marker` executes only:

```sql
SELECT 1 AS redbeaver_marker;
```

## Pacu behavior

Only read-only enumeration modules are allowlisted. Any module outside the allowlist raises an error before execution.
