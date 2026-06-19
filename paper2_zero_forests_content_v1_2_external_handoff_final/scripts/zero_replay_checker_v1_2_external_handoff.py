#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys, hashlib

def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda:f.read(1024*1024), b''): h.update(ch)
    return h.hexdigest()

def load(p):
    try: return json.loads(pathlib.Path(p).read_text())
    except Exception as e: return {'review_pass':False,'issues':[{'code':'READ_ERROR','path':str(p),'error':repr(e)}]}

def run(cmd, out):
    p=subprocess.run(cmd,capture_output=True,text=True)
    return p, load(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--out',required=True); ap.add_argument('--md-out')
    args=ap.parse_args(); root=pathlib.Path(args.package_root).resolve(); bundle=root/'evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json'
    core_out=root/'outputs/replay_report_v1_2_core_inherited_v1_1.inner.json'
    pc,core=run([sys.executable,str(root/'scripts/zero_replay_checker_v1_1_evidence_depth.py'),'--package-root',str(root),'--bundle','evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json','--out',str(core_out)],core_out)
    val_out=root/'outputs/external_ci_validation_v1_2_local_preflight.inner.json'
    pv,val=run([sys.executable,str(root/'scripts/external_ci_record_validator_v1_2.py'),'--package-root',str(root),'--record','external_ci/external_ci_results.v1_2.local_preflight.json','--out',str(val_out)],val_out)
    strict_out=root/'outputs/external_ci_validation_v1_2_require_real_expected_fail.inner.json'
    ps,strict=run([sys.executable,str(root/'scripts/external_ci_record_validator_v1_2.py'),'--package-root',str(root),'--record','external_ci/external_ci_results.v1_2.local_preflight.json','--out',str(strict_out),'--require-real'],strict_out)
    proof=load(root/'outputs/proof_assistant_compile_probe_v1_2.json')
    rec=load(root/'external_ci/external_ci_results.v1_2.local_preflight.json')
    bundle_data=load(bundle)
    ext=bundle_data.get('external_handoff_v1_2',{}) if isinstance(bundle_data,dict) else {}
    gates={
      'EH1_no_manuscript_dir': not (root/'paper').exists(),
      'EH2_inherited_v1_1_replay_pass': bool(core.get('review_pass')) and pc.returncode==0,
      'EH3_local_preflight_record_validates': bool(val.get('review_pass')) and pv.returncode==0,
      'EH4_require_real_rejects_local_preflight': ps.returncode!=0 and strict.get('review_pass') is False,
      'EH5_no_false_real_external_claim': rec.get('real_external_run') is False and rec.get('summary',{}).get('compiled_pass_external') is False,
      'EH6_proof_assistant_probe_no_overclaim': bool(proof.get('review_pass')) and not (proof.get('compiled_pass') and not rec.get('real_external_run')),
      'EH7_handoff_files_present': all((root/p).exists() for p in ['.github/workflows/paper2_zero_forest_external_ci.yml','external_ci/external_ci_results.v1_2.template.json','scripts/external_ci_record_builder_v1_2.py','scripts/external_ci_record_validator_v1_2.py','external_ci/README_REAL_EXTERNAL_RUN_v1_2.md']),
      'EH8_bundle_links_parent_v1_1': ext.get('parent_v1_1_bundle_sha256') and ext.get('real_external_run_claimed') is False,
      'EH9_manifest_and_checksums_present': (root/'release/v1_2_external_handoff_manifest.json').exists() and (root/'release/CHECKSUMS.sha256').exists(),
      'EH10_guardrails_present': all((root/p).exists() for p in ['NO_MANUSCRIPT_SCOPE.md','content/54_v1_2_external_evidence_handoff_scope.md','content/58_external_run_claim_posture_v1_2.md'])
    }
    issues=[{'gate':k,'code':'EXTERNAL_HANDOFF_GATE_FAILED'} for k,v in gates.items() if not v]
    rep={'title':'Paper2 Zero Forests v1.2 external-handoff replay report','review_pass':len(issues)==0,'strict_level':'Level-B+ external handoff preflight over v1.1 evidence-depth','canonical_bundle':'evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json','canonical_bundle_sha256':sha_file(bundle),'counts':core.get('counts',{}),'external_handoff_counts':{'local_preflight_jobs':len(rec.get('jobs',[])) if isinstance(rec,dict) else 0,'real_external_run_claimed':bool(rec.get('real_external_run')) if isinstance(rec,dict) else False,'proof_assistant_compile_attempted':bool(proof.get('compile_attempted')),'proof_assistant_compiled_pass':bool(proof.get('compiled_pass')),'strict_real_validator_rejected_local_preflight':ps.returncode!=0},'gates':{**core.get('gates',{}),**gates},'external_handoff_gates':gates,'claim_posture':{'allowed':['Level-B+ selected zero forest content evidence inherited from v1.1','hosted-CI handoff workflow and strict record validator','local preflight of external-evidence plumbing','tamper rejection for false real-run claims'],'not_claimed':['real external CI success','Lean/Coq/Rocq compiled theorem unless a hosted compile record is supplied','full tensor CAS verification','full componentwise Bianchi theorem','universal zero-decision procedure']},'issue_count':len(issues),'warning_count':int(core.get('warning_count',0)),'issues':issues,'warnings':core.get('warnings',[])}
    out=pathlib.Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
    if args.md_out:
        lines=['# Replay report v1.2 external handoff','',f"review_pass: `{rep['review_pass']}`",f"real_external_run_claimed: `{rep['external_handoff_counts']['real_external_run_claimed']}`",f"strict_real_validator_rejected_local_preflight: `{rep['external_handoff_counts']['strict_real_validator_rejected_local_preflight']}`",'', '| gate | pass |','|---|---:|']+[f"| `{k}` | `{v}` |" for k,v in gates.items()]
        pathlib.Path(args.md_out).write_text('\n'.join(lines)+'\n')
    print(json.dumps({'review_pass':rep['review_pass'],'real_external_run_claimed':rep['external_handoff_counts']['real_external_run_claimed'],'issue_count':len(issues),'warning_count':rep['warning_count']},indent=2))
    return 0 if rep['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
