#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, subprocess, sys
from pathlib import Path

def run_val(root, rec, name):
    cases=root/'outputs/tamper_cases_v1_1_evidence_depth'; cases.mkdir(parents=True, exist_ok=True)
    rp=cases/f'{name}.json'; op=cases/f'{name}.ingestion_report.json'; mp=cases/f'{name}.ingestion_report.md'
    rp.write_text(json.dumps(rec,indent=2)+'\n')
    p=subprocess.run([sys.executable, str(root/'scripts/external_ci_record_validator_v1_1.py'), '--package-root', str(root), '--record', str(rp.relative_to(root)), '--out', str(op), '--md-out', str(mp)], capture_output=True, text=True)
    return p.returncode==0, str(op.relative_to(root)), p.stdout, p.stderr

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root', default='.'); ap.add_argument('--record', default='external_ci/external_ci_results.v1.v1_1_local_dry_run.json'); ap.add_argument('--out', required=True)
    a=ap.parse_args(); root=Path(a.package_root).resolve(); base=json.loads((root/a.record).read_text())
    cases=[]
    def add(name, expect, fn):
        rec=copy.deepcopy(base); fn(rec); actual, report, stdout, stderr=run_val(root, rec, name); cases.append({'case_id':name,'expected_pass':expect,'actual_pass':actual,'expectation_met':expect==actual,'report':report})
    add('baseline_untampered', True, lambda r: None)
    add('schema_id_mutated', False, lambda r: r.update({'schema_id':'bad'}))
    add('raw_log_hash_mutated', False, lambda r: r['jobs'][0].update({'raw_log_sha256':'0'*64}))
    add('output_hash_mutated', False, lambda r: r['jobs'][0].update({'output_sha256':'f'*64}))
    add('required_job_deleted', False, lambda r: r['jobs'].pop(1))
    add('false_real_external_run_claim', False, lambda r: r.update({'real_external_run':True}))
    add('compiled_pass_external_overclaim', False, lambda r: r['summary'].update({'compiled_pass_external':True}))
    add('limitations_deleted', False, lambda r: r.update({'limitations':[]}))
    add('bad_status_vocab', False, lambda r: r['jobs'][0].update({'status':'maybe'}))
    malicious=[c for c in cases if not c['expected_pass']]
    rep={'schema_id':'tamper_suite_v1_1_evidence_depth_report.v1','baseline_pass':cases[0]['actual_pass'],'total_cases':len(cases),'malicious_cases':len(malicious),'malicious_cases_rejected':sum(1 for c in malicious if not c['actual_pass']),'all_expectations_met':all(c['expectation_met'] for c in cases),'cases':cases}
    out=Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(rep,indent=2)+'\n')
    out.with_suffix('.md').write_text(f"# Tamper suite v1.1 evidence depth\n\nbaseline_pass: `{rep['baseline_pass']}`\n\ntotal_cases: `{rep['total_cases']}`\n\nmalicious_cases_rejected: `{rep['malicious_cases_rejected']} / {rep['malicious_cases']}`\n\nall_expectations_met: `{rep['all_expectations_met']}`\n")
    print(json.dumps({'all_expectations_met':rep['all_expectations_met'],'malicious_cases_rejected':rep['malicious_cases_rejected'],'malicious_cases':rep['malicious_cases']})); return 0 if rep['all_expectations_met'] else 1
if __name__=='__main__': raise SystemExit(main())
