# Active-Safe Architecture Guide

Your service path is roughly:

```text
User
  → Cloudflare
  → CloudFront
  → WAF
  → ALB
  → private EC2 services
  → RDS
```

Security visibility is collected into CloudWatch/CloudTrail/S3 and then consumed by SIEM/SOAR.

`redbeaver` should therefore be run from multiple positions:

## 1. External runner

Use this for edge and web-facing markers.

```bash
python run.py --scenario ddos_marker
python run.py --scenario credential_stuffing_marker
python run.py --scenario webshell_marker
```

Expected logs:

- Cloudflare request logs
- CloudFront access logs
- WAF logs
- ALB access logs
- application auth/upload logs

## 2. Private app EC2

Use this for internal host behavior.

```bash
python run.py --scenario c2_marker
python run.py --scenario ransomware_marker
python run.py --scenario db_stealer_marker
```

Expected logs:

- EC2 process/network logs
- NAT egress logs
- DNS logs
- Velociraptor/FIM/Wazuh file events
- RDS connect/select logs
- optional S3 PutObject and CloudTrail

## 3. Bastion / DevOps runner

Use this for cloud-control-plane behavior.

```bash
python run.py --scenario supply_chain_marker
python run.py --scenario github_secret_marker
```

Expected logs:

- STS GetCallerIdentity
- IAM ListAccountAliases
- optional Pacu read-only enumeration
- CloudTrail management events
