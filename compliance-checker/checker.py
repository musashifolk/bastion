import docker
import json
import sys
from datetime import datetime, timezone
from rules.docker_baseline import run_baseline_checks
from rules.mtls_check import check_mtls

def main():
    client = docker.from_env()
    containers = client.containers.list()

    results = []
    for ct in containers:
        results.append(run_baseline_checks(ct))

    mtls_result = check_mtls()
    results.append(mtls_result)

    score = sum(1 for r in results for f in r["findings"] if f["status"] == "PASS")
    total = sum(len(r["findings"]) for r in results)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": f"{score}/{total}",
        "pass_rate": round((score / total) * 100, 2) if total else 0,
        "results": results,
    }

    with open("reports/report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))

    if report["pass_rate"] < 100:
        sys.exit(1)

if __name__ == "__main__":
    main()