import subprocess
import json

def run_trivy_scan(image: str) -> dict:
    try:
        result = subprocess.run(
            [
                "trivy", "image",
                "--format", "json",
                "--quiet",
                "--severity", "CRITICAL",
                image
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        data = json.loads(result.stdout)
        criticals = _count_criticals(data)
        return {
            "check": "no_unresolved_criticals",
            "status": "FAIL" if criticals > 0 else "PASS",
            "detail": f"critical_vulnerabilities={criticals}, image={image}"
        }
    except FileNotFoundError:
        return {
            "check": "no_unresolved_criticals",
            "status": "SKIP",
            "detail": "trivy not installed on this host"
        }
    except Exception as e:
        return {
            "check": "no_unresolved_criticals",
            "status": "FAIL",
            "detail": f"scan error: {e}"
        }

def _count_criticals(data: dict) -> int:
    count = 0
    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities") or []:
            if vuln.get("Severity") == "CRITICAL":
                count += 1
    return count