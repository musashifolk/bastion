# mTLS Setup

This directory contains the Traefik configuration for enforcing mutual TLS across all internal service routes using certificates issued by the step-ca PKI.

## How it works

1. step-ca (in `pki/step-ca/`) acts as the internal CA and issues certs
2. Traefik is configured to require a valid client cert signed by that CA on every internal route
3. Services like Grafana, Prometheus, and Portainer are only reachable if the client presents a valid cert

## Setup

**1. Start the internal CA first**
```bash
cd pki/step-ca
docker compose up -d
```

**2. Issue a server cert for Traefik**
```bash
step ca certificate "traefik.internal" traefik.crt traefik.key
```

**3. Issue a client cert for each service consumer**
```bash
step ca certificate "client" client.crt client.key
```

**4. Place certs in the right location**

Traefik expects certs at the paths defined in `traefik-mtls/dynamic.yml`. Update those paths to match where you placed your certs.

**5. Start Traefik**
```bash
docker compose up -d
```

## Verifying mTLS

The compliance checker verifies mTLS is active by connecting to Traefik on port 443 and checking the cert issuer matches `BastionCA`. Run it with:

```bash
cd compliance-checker
python checker.py
```

A passing `mtls_enforced` check confirms mTLS is working.