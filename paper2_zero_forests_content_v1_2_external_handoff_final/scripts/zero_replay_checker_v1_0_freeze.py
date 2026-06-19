#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys, hashlib

def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-root', default=None)
    ap.add_argument('--bundle', default=None)
    ap.add_argument('--out', required=True)
    a=ap.parse_args()
    root=pathlib.Path(a.package_root).resolve() if a.package_root else pathlib.Path(__file__).resolve().parents[1]
    bundle=pathlib.Path(a.bundle).resolve() if a.bundle else root/'evidence/examples/zero_bundle_v1_2.v1_0_freeze.json'
    inner=root/'outputs/replay_report_v1_0_freeze.inner_v0_9.json'
    proc=subprocess.run([sys.executable, str(root/'scripts/zero_replay_checker_v0_9_typeflow.py'), '--bundle', str(bundle), '--out', str(inner)], capture_output=True, text=True)
    base=json.loads(inner.read_text()) if inner.exists() else {'review_pass':False,'counts':{},'gates':{},'issues':[{'code':'INNER_MISSING'}]}
    data=json.loads(bundle.read_text())
    manifest=json.loads((root/'release/v1_0_freeze_manifest.json').read_text())
    flrw=next((c for c in data.get('certificates',[]) if c.get('claim_id')=='zero.flrw.contracted_bianchi_divG0'), None)
    route_ids=[r.get('route_id') for r in (flrw or {}).get('routes',[])]
    gates={
        'FZ1_no_manuscript_dir': not (root/'paper').exists(),
        'FZ2_bundle_hash_matches_manifest': sha_file(bundle)==manifest.get('canonical_bundle_sha256'),
        'FZ3_inner_replay_pass': bool(base.get('review_pass')) and proc.returncode==0,
        'FZ4_canonical_flrw_route_present': manifest.get('metrics',{}).get('flrw_primary_route') in route_ids,
        'FZ5_level_b_plus_layers_present': bool(flrw) and len(flrw.get('tensor_subleaves',[]))>=6 and len(flrw.get('typed_dependency_flow',{}).get('typed_dependency_edges',[]))>=10,
        'FZ6_guardrail_docs_present': all((root/p).exists() for p in ['content/40_level_b_plus_trust_statement_v1_0.md','content/41_freeze_claim_ledger_v1_0.md','NO_MANUSCRIPT_SCOPE.md']),
    }
    issues=[] if all(gates.values()) else [{'gate':k,'code':'FREEZE_GATE_FAILED'} for k,v in gates.items() if not v]
    report={
        'title':'Paper2 Zero Forests v1.0 freeze-final replay report',
        'review_pass': bool(base.get('review_pass')) and all(gates.values()),
        'strict_level':'Level-B+ content freeze over v0.9 typed dependency flow',
        'canonical_bundle': str(bundle.relative_to(root)),
        'canonical_bundle_sha256': sha_file(bundle),
        'counts': base.get('counts',{}),
        'gates': {**base.get('gates',{}), **gates},
        'freeze_gates': gates,
        'issue_count': int(base.get('issue_count',0))+len(issues),
        'warning_count': int(base.get('warning_count',0)),
        'issues': base.get('issues',[])+issues,
        'warnings': base.get('warnings',[]),
    }
    out=pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'review_pass':report['review_pass'],'issue_count':report['issue_count'],'warning_count':report['warning_count']},indent=2))
    return 0 if report['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
