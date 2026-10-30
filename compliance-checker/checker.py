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
    pass_rate = round((score / total) * 100, 2) if total else 0

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": f"{score}/{total}",
        "pass_rate": pass_rate,
        "results": results,
    }

    with open("reports/report.json", "w") as f:
        json.dump(report, f, indent=2)

    with open("reports/report.html", "w") as f:
        f.write(_render_html(report))

    print(json.dumps(report, indent=2))

    if pass_rate < 100:
        sys.exit(1)

def _render_html(report):
    rows = ""
    for r in report["results"]:
        for f in r["findings"]:
            color = "#2ecc71" if f["status"] == "PASS" else "#e74c3c"
            rows += f"""
            <tr>
                <td>{r['container']}</td>
                <td>{f['check']}</td>
                <td style="color:{color};font-weight:bold">{f['status']}</td>
                <td>{f['detail']}</td>
            </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Bastion Compliance Report</title>
<style>
  body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 2rem; }}
  h1 {{ color: #58a6ff; }}
  .meta {{ margin-bottom: 1.5rem; color: #8b949e; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; border-bottom: 1px solid #30363d; padding: 0.5rem; color: #8b949e; }}
  td {{ padding: 0.5rem; border-bottom: 1px solid #21262d; }}
  .score {{ font-size: 1.4rem; margin-bottom: 0.5rem; }}
</style>
</head>
<body>
<h1>Bastion — Compliance Report</h1>
<div class="meta">Generated: {report['generated_at']}</div>
<div class="score">Score: <strong>{report['score']}</strong> &nbsp;|&nbsp; Pass rate: <strong>{report['pass_rate']}%</strong></div>
<table>
  <thead><tr><th>Container</th><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</body>
</html>"""

if __name__ == "__main__":
    main()