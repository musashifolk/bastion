import docker
from datetime import datetime, timezone, timedelta
from rules.trivy_check import run_trivy_scan

IMAGE_AGE_LIMIT_DAYS = 90

def run_baseline_checks(container):
    findings = []
    inspect = container.client.api.inspect_container(container.id)
    config = inspect["HostConfig"]

    user = inspect["Config"].get("User", "")
    findings.append({
        "check": "no_root_user",
        "status": "FAIL" if user in ("", "0", "root") else "PASS",
        "detail": f"user='{user}'"
    })

    privileged = config.get("Privileged", False)
    findings.append({
        "check": "not_privileged",
        "status": "FAIL" if privileged else "PASS",
        "detail": f"privileged={privileged}"
    })

    mem = config.get("Memory", 0)
    findings.append({
        "check": "memory_limit_set",
        "status": "PASS" if mem > 0 else "FAIL",
        "detail": f"memory={mem}"
    })

    cpu = config.get("NanoCpus", 0)
    findings.append({
        "check": "cpu_limit_set",
        "status": "PASS" if cpu > 0 else "FAIL",
        "detail": f"nano_cpus={cpu}"
    })

    restart = config.get("RestartPolicy", {}).get("Name", "")
    findings.append({
        "check": "restart_policy_set",
        "status": "PASS" if restart and restart != "no" else "FAIL",
        "detail": f"restart_policy='{restart}'"
    })

    ports = config.get("PortBindings") or {}
    risky = [p for p in ports if p.startswith("9090")]
    findings.append({
        "check": "no_unnecessary_host_ports",
        "status": "FAIL" if risky else "PASS",
        "detail": f"exposed={list(ports.keys())}"
    })

    findings.append(_check_image_age(container))

    image = container.image.tags[0] if container.image.tags else None
    if image:
        findings.append(run_trivy_scan(image))

    return {
        "container": container.name,
        "image": image or "untagged",
        "findings": findings
    }

def _check_image_age(container):
    try:
        created_str = container.image.attrs.get("Created", "")
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - created
        stale = age > timedelta(days=IMAGE_AGE_LIMIT_DAYS)
        return {
            "check": "image_not_stale",
            "status": "FAIL" if stale else "PASS",
            "detail": f"image_age_days={age.days}"
        }
    except Exception as e:
        return {
            "check": "image_not_stale",
            "status": "FAIL",
            "detail": f"could not determine image age: {e}"
        }