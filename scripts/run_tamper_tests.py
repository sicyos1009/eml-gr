#!/usr/bin/env python3
from __future__ import annotations
import copy, json, subprocess, sys, tempfile
from pathlib import Path
from _common import read_json, write_json


def validate(path, cwd):
    return subprocess.run([sys.executable,'scripts/validate_external_ci_results.py',str(path),'--base','.'], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def main() -> int:
    root=Path('.').resolve()
    base=root/'examples/external_ci_results.example.v1.json'
    if not base.exists():
        subprocess.run([sys.executable,'scripts/simulate_fixture_records.py','--root','.'], cwd=root, check=True)
    bundle=read_json(base)
    cases=[]
    with tempfile.TemporaryDirectory() as td:
        t=Path(td)
        # Baseline
        p=t/'baseline.json'; write_json(p,bundle); r=validate(p,root); cases.append({'case':'baseline_should_pass','passed':r.returncode==0})
        # result hash mismatch
        b=copy.deepcopy(bundle); b['records'][0]['result_hash']='f'*16; p=t/'bad_hash.json'; write_json(p,b); r=validate(p,root); cases.append({'case':'result_hash_mismatch_should_fail','passed':r.returncode!=0})
        # exit/status mismatch
        b=copy.deepcopy(bundle); b['records'][0]['command']['exit_code']=1; p=t/'bad_exit.json'; write_json(p,b); r=validate(p,root); cases.append({'case':'status_exit_mismatch_should_fail','passed':r.returncode!=0})
        # real external without URL
        b=copy.deepcopy(bundle); b['records'][0]['provenance']['real_external_run']=True; b['records'][0]['provenance']['kind']='external_ci'; b['records'][0]['provenance']['run_url']=None; b['records'][0]['provenance']['commit_sha']='abc123'; p=t/'bad_real.json'; write_json(p,b); r=validate(p,root); cases.append({'case':'real_run_without_url_should_fail','passed':r.returncode!=0})
        # malformed sha
        b=copy.deepcopy(bundle); b['records'][0]['artifact_package_sha256']='not-a-sha'; p=t/'bad_sha.json'; write_json(p,b); r=validate(p,root); cases.append({'case':'artifact_sha_malformed_should_fail','passed':r.returncode!=0})
    report={'cases':cases,'baseline_passed':cases[0]['passed'],'all_tampered_failed':all(c['passed'] for c in cases[1:]),'review_pass':all(c['passed'] for c in cases)}
    write_json(root/'outputs/v39_tamper_report.json', report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['review_pass'] else 1
if __name__=='__main__':
    raise SystemExit(main())
