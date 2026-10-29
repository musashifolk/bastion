import docker
from datetime import datetime, timezone

def run_baseline_checks(container):
    findings = []
    inspect = container.client.api.inspect_container(container.id)
    config = inspect["HostConfig"]

    # root user check
    user = inspect["Config"].get("User", "")
    findings.append({
        "check": "no_root_user",
        "status": "FAIL" if user in ("", "0", "root") else "PASS",
        "detail": f"user='{user}'"
    })

    # privileged check
    privileged = config.get("Privileged", False)
    findings.append({
        "check": "not_privileged",
        "status": "FAIL" if privileged else "PASS",
        "detail": f"privileged={privileged}"
    })

    # memory limit
    mem = config.get("Memory", 0)
    findings.append({
        "check": "memory_limit_set",
        "status": "PASS" if mem > 0 else "FAIL",
        "detail": f"memory={mem}"
    })

    # cpu limit
    cpu = config.get("NanoCpus", 0)
    findings.append({
        "check": "cpu_limit_set",
        "status": "PASS" if cpu > 0 else "FAIL",
        "detail": f"nano_cpus={cpu}"
    })

    # restart policy
    restart = config.get("RestartPolicy", {}).get("Name", "")
    findings.append({
        "check": "restart_policy_set",
        "status": "PASS" if restart and restart != "no" else "FAIL",
        "detail": f"restart_policy='{restart}'"
    })

    # unnecessary ports exposed to host
    ports = config.get("PortBindings") or {}
    risky = [p for p in ports if p.startswith("9090")]
    findings.append({
        "check": "no_unnecessary_host_ports",
        "status": "FAIL" if risky else "PASS",
        "detail": f"exposed={list(ports.keys())}"
    })

    return {
        "container": container.name,
        "image": container.image.tags[0] if container.image.tags else "untagged",
        "findings": findings
    }