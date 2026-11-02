import ssl
import socket

TRAEFIK_HOST = "localhost"
TRAEFIK_PORT = 443
EXPECTED_CA = "BastonCA"

def check_mtls():
    result = _verify_tls_cert()
    return {
        "container": "traefik",
        "image": "traefik",
        "findings": [result]
    }

def _verify_tls_cert():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with ctx.wrap_socket(
            socket.create_connection((TRAEFIK_HOST, TRAEFIK_PORT), timeout=3),
            server_hostname=TRAEFIK_HOST
        ) as s:
            cert = s.getpeercert()
            issuer = dict(x[0] for x in cert.get("issuer", []))
            ca_name = issuer.get("organizationName", "")
            signed_by_bastion = EXPECTED_CA in ca_name

            return {
                "check": "mtls_enforced",
                "status": "PASS" if signed_by_bastion else "FAIL",
                "detail": f"cert_issuer='{ca_name}', expected='{EXPECTED_CA}'"
            }
    except ConnectionRefusedError:
        return {
            "check": "mtls_enforced",
            "status": "FAIL",
            "detail": "traefik not reachable on port 443"
        }
    except Exception as e:
        return {
            "check": "mtls_enforced",
            "status": "FAIL",
            "detail": f"tls check failed: {e}"
        }