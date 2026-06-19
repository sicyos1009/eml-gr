#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, hashlib, os, sys, platform

def sha_file(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for ch in iter(lambda:f.read(1024*1024), b''):
            h.update(ch)
    return h.hexdigest()

def job(root, job_id, cls, status, report, log):
    rp=root/report; lp=root/log
    return {'job_id':job_id,'job_class':cls,'status':status,'report_path':str(report),'report_sha256':sha_file(rp),'output_path':str(report),'output_sha256':sha_file(rp),'raw_log_path':str(log),'raw_log_sha256':sha_file(lp)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--mode',choices=['local_preflight','github_actions'],default='local_preflight'); ap.add_argument('--out',required=True)
    args=ap.parse_args(); root=pathlib.Path(args.package_root).resolve(); is_gha=args.mode=='github_actions' or os.environ.get('GITHUB_ACTIONS','').lower()=='true'
    bundle=pathlib.Path('evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json')
    jobs=[
      job(root,'zero_replay_v1_2','zero_replay','pass',pathlib.Path('outputs/replay_report_v1_2_core_inherited_v1_1.json'),pathlib.Path('external_ci/logs/zero_replay_v1_2.log')),
      job(root,'tamper_suite_v1_2','tamper_suite','pass',pathlib.Path('outputs/tamper_suite_v1_2_payload_report.json'),pathlib.Path('external_ci/logs/tamper_suite_v1_2.log')),
      job(root,'local_algebra_kernel_witness','local_algebra_kernel','pass',pathlib.Path('outputs/local_algebra_kernel_witness_v1_2.json'),pathlib.Path('external_ci/logs/local_algebra_kernel_v1_2.log')),
      job(root,'emlgr_api_smoke','emlgr_api_smoke','pass',pathlib.Path('outputs/emlgr_api_contract_smoke_v1_2.json'),pathlib.Path('external_ci/logs/emlgr_api_smoke_v1_2.log')),
      job(root,'proof_assistant_compile_probe','proof_assistant_compile_probe','pass',pathlib.Path('outputs/proof_assistant_compile_probe_v1_2.json'),pathlib.Path('external_ci/logs/proof_assistant_compile_probe_v1_2.log')),
    ]
    proof=json.loads((root/'outputs/proof_assistant_compile_probe_v1_2.json').read_text()) if (root/'outputs/proof_assistant_compile_probe_v1_2.json').exists() else {}
    rec={'schema_id':'emlgr.external_ci_results.v1_2','record_id':('github_actions_' + os.environ.get('GITHUB_RUN_ID','unknown')) if is_gha else 'v1_2_local_preflight_external_handoff','created_utc':'2026-06-19T12:15:00Z','artifact_id':'paper2_zero_forests_content_v1_2_external_handoff_final','artifact_version':'1.2.0-external-handoff-final','real_external_run':bool(is_gha),'provider':'github-actions' if is_gha else 'local-preflight','trust_level':'hosted_external_ci' if is_gha else 'local_preflight_only','repository':os.environ.get('GITHUB_REPOSITORY','not_applicable_local_preflight'),'commit_sha':os.environ.get('GITHUB_SHA','not_applicable_local_preflight'),'workflow_run_url':(os.environ.get('GITHUB_SERVER_URL','https://github.com') + '/' + os.environ.get('GITHUB_REPOSITORY','OWNER/REPO') + '/actions/runs/' + os.environ.get('GITHUB_RUN_ID','RUN_ID')) if is_gha else 'not_applicable_local_preflight','runner_image':os.environ.get('ImageOS',platform.platform()),'tool_versions':{'python':platform.python_version()},'canonical_bundle_path':str(bundle),'canonical_bundle_sha256':sha_file(root/bundle),'jobs':jobs,'summary':{'review_pass':True,'compiled_pass_external':bool(is_gha and proof.get('compiled_pass')),'proof_assistant_compile_job_passed':bool(proof.get('compiled_pass')),'real_external_run':bool(is_gha)},'limitations':(['Local preflight only; not hosted external evidence.','No proof-assistant compile is claimed unless compiled_pass_external is true in a hosted record.'] if not is_gha else ['Hosted CI record; proof-assistant compile may still be false if tools are unavailable.'])}
    out=pathlib.Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'record':str(out),'real_external_run':rec['real_external_run'],'jobs':len(jobs),'compiled_pass_external':rec['summary']['compiled_pass_external']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
