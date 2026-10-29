import socket

TRAEFIK_HOST = "localhost"
TRAEFIK_PORT = 8080

def check_mtls():
    reachable = _traefik_reachable()

    return {
        "container": "traefik",
        "findings": [
            {
                "check": "mtls_enforced",
                "status": "FAIL",
                "detail": f"traefik_reachable={reachable}, mTLS not configured yet"
            }
        ]
    }

def _traefik_reachable():
    try:
        s = socket.create_connection((TRAEFIK_HOST, TRAEFIK_PORT), timeout=2)
        s.close()
        return True
    except OSError:
        return False