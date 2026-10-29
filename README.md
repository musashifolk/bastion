# Bastion

Bastion is a homelab security project built around a simple loop: audit your infrastructure, fix what's broken, verify the fix.

It does two things. First, a Python-based compliance checker inspects your running Docker environment and produces a report flagging containers with missing limits, bad restart policies, root users, and missing mTLS. Second, an internal PKI built on step-ca issues and rotates TLS certificates, and Traefik is configured to enforce mTLS across all internal service routes. Once Part 2 is complete, re-running the checker should pass every check.

CI runs on every push. If the compliance score drops, the pipeline fails.

---

## Part 1 — Compliance Checker

```bash
cd compliance-checker
pip install -r requirements.txt
python checker.py
```

Report is saved to `compliance-checker/reports/report.json`.

---

## Part 2 — Internal PKI

```bash
cd pki/step-ca
docker compose up -d
```

---

## Stack

Python · Docker · step-ca · Traefik v3 · GitHub Actions · Debian 13