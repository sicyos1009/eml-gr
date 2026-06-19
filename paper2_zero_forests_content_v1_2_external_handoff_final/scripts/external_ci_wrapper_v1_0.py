#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, platform, sys, time

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--package-root', default='.')
    a=ap.parse_args(); root=pathlib.Path(a.package_root).resolve(); out=pathlib.Path(a.out)
    replay=json.loads((root/'outputs/replay_report_v1_0_freeze.json').read_text())
    rec={'schema_id':'external_ci_results.v1','record_kind':'local_dry_run','real_external_run':False,'external_provider':'local-dry-run-placeholder','created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'python_version':sys.version,'platform':platform.platform(),'replay_review_pass':bool(replay.get('review_pass')),'upgrade_required':['commit SHA','workflow run id','raw log SHA256','real_external_run=true']}
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(rec,indent=2)+'
')
    print(json.dumps({'real_external_run':False,'replay_review_pass':rec['replay_review_pass']}))
if __name__=='__main__': main()
