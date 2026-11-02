# Hardening Checklist

Work through this before running the compliance checker. Every item here maps to a check in the tool.

---

## Docker

- [ ] No container runs as root — set `user: 1000:1000` in compose
- [ ] No container has `privileged: true`
- [ ] Every container has `mem_limit` and `cpus` set in compose
- [ ] Every container has `restart: unless-stopped`
- [ ] Prometheus port 9090 not bound to host — remove from `ports:` in compose
- [ ] All images pulled or rebuilt within last 90 days

## Vulnerability Scanning

- [ ] Trivy installed on the homelab machine
- [ ] Run `trivy image <image>` on every container image
- [ ] No unresolved CRITICAL CVEs — update or replace affected images

## mTLS

- [ ] step-ca running and reachable at `https://step-ca:9000`
- [ ] Root CA cert exported from step-ca to `/certs/root_ca.crt`
- [ ] Traefik config replaced with `mtls/traefik-mtls/traefik.yml` and `dynamic.yml`
- [ ] All internal services on `traefik_default` network
- [ ] Traefik restarted and serving certs from step-ca
- [ ] Re-run compliance checker — `mtls_enforced` check passes