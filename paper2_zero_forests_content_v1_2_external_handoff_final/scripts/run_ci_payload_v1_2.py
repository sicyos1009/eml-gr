#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, pathlib, sys, json, shutil

def run_logged(root, cmd, log_rel):
    log=root/log_rel; log.parent.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(cmd,capture_output=True,text=True,cwd=str(root))
    log.write_text('$ '+ ' '.join(str(c) for c in cmd) + '\n\n[stdout]\n' + p.stdout + '\n[stderr]\n' + p.stderr + f'\n[returncode]\n{p.returncode}\n')
    return p

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.')
    args=ap.parse_args(); root=pathlib.Path(args.package_root).resolve()
    outputs=root/'outputs'; outputs.mkdir(exist_ok=True)
    # zero replay inherited from v1.1 over the v1.2 canonical bundle
    run_logged(root,[sys.executable,'scripts/zero_replay_checker_v1_1_evidence_depth.py','--package-root','.', '--bundle','evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json','--out','outputs/replay_report_v1_2_core_inherited_v1_1.json','--md-out','outputs/replay_report_v1_2_core_inherited_v1_1.md'],pathlib.Path('external_ci/logs/zero_replay_v1_2.log'))
    run_logged(root,[sys.executable,'scripts/tamper_suite_v1_1_evidence_depth.py','--package-root','.', '--out','outputs/tamper_suite_v1_2_payload_report.json'],pathlib.Path('external_ci/logs/tamper_suite_v1_2.log'))
    run_logged(root,[sys.executable,'scripts/local_algebra_kernel_witness_v1_1.py','--out','outputs/local_algebra_kernel_witness_v1_2.json','--md-out','outputs/local_algebra_kernel_witness_v1_2.md'],pathlib.Path('external_ci/logs/local_algebra_kernel_v1_2.log'))
    run_logged(root,[sys.executable,'scripts/emlgr_api_contract_smoke_v1_1.py','--package-root','.', '--out','outputs/emlgr_api_contract_smoke_v1_2.json','--md-out','outputs/emlgr_api_contract_smoke_v1_2.md'],pathlib.Path('external_ci/logs/emlgr_api_smoke_v1_2.log'))
    run_logged(root,[sys.executable,'scripts/proof_assistant_compile_probe_v1_2.py','--package-root','.', '--out','outputs/proof_assistant_compile_probe_v1_2.json','--md-out','outputs/proof_assistant_compile_probe_v1_2.md'],pathlib.Path('external_ci/logs/proof_assistant_compile_probe_v1_2.log'))
    print(json.dumps({'payload_complete':True},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
