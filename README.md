# Bastion

A homelab security project built around a simple loop: audit your infrastructure, fix what's broken, verify the fix.

Bastion does two things. First, a Python based compliance checker inspects your running Docker environment and produces a report flagging containers with missing limits, bad restart policies, root users, stale images, and missing mTLS. Second, an internal PKI built on step-ca issues and rotates TLS certificates, and Traefik enforces mTLS across all internal service routes. Once Parts 2 and 3 are complete, re running the checker passes every check.

CI runs on every push. If the compliance score drops, the pipeline fails.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/musashifolk/bastion
cd bastion

# 2. Start the internal CA
make up-pki

# 3. Run the compliance checker
make check

# 4. View the report
make report
```

> Run Parts 2 and 3 in order. The mTLS check will FAIL until step-ca is running and Traefik is configured with certs from it.

---

## Part 1 — Compliance Checker

Checks every running container for:

| Check | Description |
|-------|-------------|
| `no_root_user` | Container must not run as root |
| `not_privileged` | Privileged mode must be disabled |
| `memory_limit_set` | Memory limit must be configured |
| `cpu_limit_set` | CPU limit must be configured |
| `restart_policy_set` | Restart policy must not be `no` |
| `no_unnecessary_host_ports` | Only ports 80 and 443 allowed on host |
| `image_not_stale` | Image must not be older than 90 days |
| `no_unresolved_criticals` | No CRITICAL CVEs via Trivy |
| `mtls_enforced` | Traefik must present a cert signed by BastionCA |

Outputs `reports/report.json` for CI and `reports/report.html` for human review.

```bash
make check        # run against live containers
make dry-run      # run with fake data, no Docker required
```

---

## Part 2 — Internal PKI

Runs step-ca as an internal certificate authority in Docker. Handles cert issuance and automatic rotation via ACME. All internal services get certs signed by BastionCA.

```bash
make up-pki
```

---

## Part 3 — mTLS Enforcement

Traefik enforces mutual TLS on all internal service routes using certificates issued by step-ca. Every service (Grafana, Prometheus, Portainer) requires a client cert signed by BastionCA. Unauthenticated requests are rejected at the proxy layer.

See [`mtls/README.md`](mtls/README.MD) for setup details.

---

## Stack

| Tool | Role |
|------|------|
| Python | Compliance checker and report generation |
| Docker | Container runtime for all services |
| Trivy | CVE scanning per container |
| step-ca | Internal certificate authority |
| Traefik v3 | Reverse proxy with mTLS enforcement |
| GitHub Actions | CI fails if compliance score drops |
| Debian 13 | Host OS |