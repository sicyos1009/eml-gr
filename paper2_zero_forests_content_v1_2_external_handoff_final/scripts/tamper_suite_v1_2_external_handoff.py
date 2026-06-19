#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, subprocess, sys
from pathlib import Path

def run_val(root, rec, name, require_real=False):
    cases=root/'outputs/tamper_cases_v1_2_external_handoff'; cases.mkdir(parents=True, exist_ok=True)
    rp=cases/f'{name}.json'; op=cases/f'{name}.validation.json'; mp=cases/f'{name}.validation.md'
    rp.write_text(json.dumps(rec,indent=2)+'\n')
    cmd=[sys.executable,str(root/'scripts/external_ci_record_validator_v1_2.py'),'--package-root',str(root),'--record',str(rp.relative_to(root)),'--out',str(op),'--md-out',str(mp)]
    if require_real: cmd.append('--require-real')
    p=subprocess.run(cmd,capture_output=True,text=True)
    return p.returncode==0, str(op.relative_to(root))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--record',default='external_ci/external_ci_results.v1_2.local_preflight.json'); ap.add_argument('--out',required=True)
    args=ap.parse_args(); root=Path(args.package_root).resolve(); base=json.loads((root/args.record).read_text())
    cases=[]
    def add(name, expect, fn, require_real=False):
        rec=copy.deepcopy(base); fn(rec); actual, report=run_val(root, rec, name, require_real); cases.append({'case_id':name,'expected_pass':expect,'actual_pass':actual,'expectation_met':expect==actual,'require_real':require_real,'report':report})
    add('baseline_local_preflight', True, lambda r: None)
    add('local_preflight_fails_require_real', False, lambda r: None, True)
    add('false_real_external_with_placeholders', False, lambda r: r.update({'real_external_run':True,'trust_level':'hosted_external_ci','provider':'github-actions'}))
    add('bad_commit_sha_for_real', False, lambda r: r.update({'real_external_run':True,'trust_level':'hosted_external_ci','provider':'github-actions','repository':'owner/repo','commit_sha':'bad','workflow_run_url':'https://github.com/owner/repo/actions/runs/1'}))
    add('local_record_claims_compiled_pass_external', False, lambda r: r['summary'].update({'compiled_pass_external':True}))
    add('raw_log_hash_mutated', False, lambda r: r['jobs'][0].update({'raw_log_sha256':'0'*64}))
    add('output_hash_mutated', False, lambda r: r['jobs'][0].update({'output_sha256':'f'*64}))
    add('required_job_class_deleted', False, lambda r: r['jobs'].pop())
    add('trust_level_mislabeled', False, lambda r: r.update({'trust_level':'hosted_external_ci'}))
    add('limitations_deleted', False, lambda r: r.update({'limitations':[]}))
    add('bad_job_status', False, lambda r: r['jobs'][0].update({'status':'maybe'}))
    add('bundle_hash_mutated', False, lambda r: r.update({'canonical_bundle_sha256':'a'*64}))
    add('compile_external_without_compile_job', False, lambda r: (r.update({'real_external_run':True,'provider':'github-actions','trust_level':'hosted_external_ci','repository':'owner/repo','commit_sha':'0123456789abcdef0123456789abcdef01234567','workflow_run_url':'https://github.com/owner/repo/actions/runs/1'}), r['summary'].update({'compiled_pass_external':True})))
    malicious=[c for c in cases if not c['expected_pass']]
    rep={'schema_id':'tamper_suite_v1_2_external_handoff_report.v1','baseline_pass':cases[0]['actual_pass'],'total_cases':len(cases),'malicious_cases':len(malicious),'malicious_cases_rejected':sum(1 for c in malicious if not c['actual_pass']),'all_expectations_met':all(c['expectation_met'] for c in cases),'cases':cases,'review_pass':all(c['expectation_met'] for c in cases)}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2)+'\n')
    out.with_suffix('.md').write_text(f"# Tamper suite v1.2 external handoff\n\nbaseline_pass: `{rep['baseline_pass']}`\n\ntotal_cases: `{rep['total_cases']}`\n\nmalicious_cases_rejected: `{rep['malicious_cases_rejected']} / {rep['malicious_cases']}`\n\nall_expectations_met: `{rep['all_expectations_met']}`\n")
    print(json.dumps({'all_expectations_met':rep['all_expectations_met'],'malicious_cases_rejected':rep['malicious_cases_rejected'],'malicious_cases':rep['malicious_cases']},indent=2))
    return 0 if rep['all_expectations_met'] else 1
if __name__=='__main__': raise SystemExit(main())
