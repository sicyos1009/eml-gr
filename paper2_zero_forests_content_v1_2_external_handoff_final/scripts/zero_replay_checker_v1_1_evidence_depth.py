#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,subprocess,sys,hashlib
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
def load(p):
 try: return json.loads(p.read_text())
 except Exception as e: return {'review_pass':False,'issues':[{'code':'READ_ERROR','path':str(p),'error':repr(e)}]}
def run(cmd,out):
 p=subprocess.run(cmd,capture_output=True,text=True); return p, load(pathlib.Path(out))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--bundle',default='evidence/examples/zero_bundle_v1_2.v1_1_evidence_depth.json'); ap.add_argument('--out',required=True); ap.add_argument('--md-out'); a=ap.parse_args(); root=pathlib.Path(a.package_root).resolve(); bundle=root/a.bundle
 core_out=root/'outputs/replay_report_v1_1_core_typeflow.inner.json'; pc,core=run([sys.executable,str(root/'scripts/zero_replay_checker_v0_9_typeflow.py'),'--bundle',str(bundle),'--out',str(core_out)], core_out)
 fz_out=root/'outputs/replay_report_v1_1_inherited_v1_0_freeze.inner.json'; pfz,fz=run([sys.executable,str(root/'scripts/zero_replay_checker_v1_0_freeze.py'),'--package-root',str(root),'--out',str(fz_out)], fz_out)
 ci_out=root/'outputs/external_ci_validation_v1_1.inner.json'; pci,ci=run([sys.executable,str(root/'scripts/external_ci_record_validator_v1_1.py'),'--package-root',str(root),'--record','external_ci/external_ci_results.v1_1.dryrun.json','--out',str(ci_out)], ci_out)
 probe=load(root/'outputs/proof_assistant_env_probe_v1_1.json'); alg=load(root/'outputs/local_algebra_kernel_witness_v1_1.json'); api=load(root/'outputs/emlgr_api_contract_smoke_v1_1.json'); data=load(bundle); mani=load(root/'release/v1_0_freeze_manifest.json'); ev=data.get('evidence_depth',{}) if isinstance(data,dict) else {}
 gates={'ED1_no_manuscript_dir':not (root/'paper').exists(),'ED2_core_typeflow_replay_pass':bool(core.get('review_pass')) and pc.returncode==0,'ED3_inherited_v1_0_freeze_pass':bool(fz.get('review_pass')) and pfz.returncode==0,'ED4_external_ci_dryrun_record_validates':bool(ci.get('review_pass')) and pci.returncode==0,'ED5_no_false_proof_assistant_compile_claim':bool(probe.get('review_pass')) and not probe.get('compile_claimed') and not probe.get('compiled_pass'),'ED6_local_algebra_kernel_witness_pass':bool(alg.get('review_pass')),'ED7_emlgr_api_smoke_pass':bool(api.get('review_pass')),'ED8_evidence_depth_links_base_hash':ev.get('base_bundle_sha256')==mani.get('canonical_bundle_sha256') and ev.get('real_external_run_claimed') is False and ev.get('proof_assistant_compile_claimed') is False,'ED9_manifest_and_checksums_present':(root/'release/v1_1_evidence_manifest.json').exists() and (root/'release/CHECKSUMS.sha256').exists(),'ED10_guardrails_present':all((root/p).exists() for p in ['NO_MANUSCRIPT_SCOPE.md','content/48_v1_1_evidence_depth_scope.md','content/52_v1_1_evidence_readiness_matrix.md'])}
 issues=[{'gate':k,'code':'EVIDENCE_DEPTH_GATE_FAILED'} for k,v in gates.items() if not v]
 evidence_counts={'external_ci_jobs':ci.get('jobs_checked',0),'proof_assistant_tools_found':sum(1 for r in probe.get('tools',{}).values() if r.get('found')) if isinstance(probe.get('tools'),dict) else 0,'local_algebra_cases':alg.get('case_count',0),'local_algebra_cases_passed':alg.get('cases_passed',0),'emlgr_claims_seen':api.get('summary',{}).get('claims',0)}
 rep={'title':'Paper2 Zero Forests v1.1 evidence-depth replay report','review_pass':len(issues)==0,'strict_level':'Level-B+ content evidence-depth over v1.0 freeze','canonical_bundle':a.bundle,'canonical_bundle_sha256':sha(bundle),'base_v1_0_bundle_sha256':mani.get('canonical_bundle_sha256'),'counts':core.get('counts',{}),'evidence_counts':evidence_counts,'gates':{**core.get('gates',{}),**gates},'evidence_depth_gates':gates,'claim_posture':{'allowed':['Level-B+ selected zero forest content evidence','dry-run external-CI provenance plumbing','local algebra-kernel witness','emlgr API skeleton'],'not_claimed':['real external CI run','Lean/Coq/Rocq compiled theorem','full tensor CAS verification','full componentwise Bianchi theorem','universal zero-decision procedure']},'issue_count':len(issues),'warning_count':int(core.get('warning_count',0)),'issues':issues,'warnings':core.get('warnings',[])}
 out=pathlib.Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
 if a.md_out:
  lines=['# Replay report v1.1 evidence-depth','',f"review_pass: `{rep['review_pass']}`",'', '| gate | pass |','|---|---:|']+[f"| `{k}` | `{v}` |" for k,v in gates.items()]
  pathlib.Path(a.md_out).write_text('\n'.join(lines)+'\n')
 print(json.dumps({'review_pass':rep['review_pass'],'evidence_counts':evidence_counts,'issue_count':len(issues),'warning_count':rep['warning_count']},indent=2,ensure_ascii=False)); return 0 if rep['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
