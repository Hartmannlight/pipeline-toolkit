"""Gate scanner results and remove secret values before artifact retention."""
import json
import sys
from pathlib import Path

def evaluate(report):
    if not isinstance(report, dict) or 'Results' not in report:
        raise ValueError('Missing Trivy Results')
    blocked, pending = [], []
    for result in report['Results'] or []:
        for finding in result.get('Vulnerabilities') or []:
            if finding.get('Severity') in ('HIGH', 'CRITICAL'):
                item = [finding.get('VulnerabilityID'), finding.get('PkgName')]
                (blocked if finding.get('FixedVersion') else pending).append(item)
        for finding in result.get('Secrets') or []:
            for key in ('Match', 'Code'):
                finding.pop(key, None)
            if finding.get('Severity') in ('HIGH', 'CRITICAL'):
                blocked.append([finding.get('RuleID'), result.get('Target')])
    return blocked, pending

if __name__ == '__main__':
    path = Path(sys.argv[1])
    report = json.loads(path.read_text())
    blocked, pending = evaluate(report)
    path.write_text(json.dumps(report, indent=2))
    print(json.dumps({'blocked': blocked, 'unpatched_requires_triage': pending}))
    raise SystemExit(bool(blocked))
