#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,hashlib,re

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--record',default='external_ci/external_ci_results.v1.v1_1_local_dry_run.json'); ap.add_argument('--out',required=True); ap.add_argument('--md-out',default=None)
    a=ap.parse_args(); root=pathlib.Path(a.package_root).resolve(); issues=[]; warnings=[]
    try:
        rec=json.loads((root/a.record).read_text())
    except Exception as e:
        rec={}; issues.append({'gate':'CI1','code':'RECORD_READ_ERROR','error':repr(e)})
    if rec.get('schema_id')!='emlgr.external_ci_results.v1_1': issues.append({'gate':'CI1','code':'BAD_SCHEMA_ID','observed':rec.get('schema_id')})
    real=bool(rec.get('real_external_run'))
    if real:
        for k in ['repository','commit_sha','workflow_run_url','runner_image','tool_versions']:
            if not rec.get(k) or str(rec.get(k)).startswith('not_applicable'):
                issues.append({'gate':'CI2','code':'MISSING_REAL_RUN_PROVENANCE','field':k})
        if not re.fullmatch(r'[0-9a-fA-F]{40}',str(rec.get('commit_sha',''))): issues.append({'gate':'CI2','code':'BAD_COMMIT_SHA'})
    else:
        if rec.get('trust_level')!='dry_run_provenance_only': issues.append({'gate':'CI2','code':'BAD_DRY_RUN_TRUST_LEVEL'})
    if not rec.get('limitations'):
        issues.append({'gate':'CI8','code':'LIMITATIONS_MISSING'})
    if rec.get('summary',{}).get('compiled_pass_external') and not real:
        issues.append({'gate':'CI8','code':'DRY_RUN_COMPILED_PASS_EXTERNAL_OVERCLAIM'})
    bp=root/rec.get('canonical_bundle_path','') if rec.get('canonical_bundle_path') else None
    if not bp or not bp.exists(): issues.append({'gate':'CI3','code':'BUNDLE_MISSING'})
    elif sha(bp)!=rec.get('canonical_bundle_sha256'): issues.append({'gate':'CI3','code':'BUNDLE_HASH_MISMATCH','reported':rec.get('canonical_bundle_sha256'),'recomputed':sha(bp)})
    jobs=rec.get('jobs',[]); ok_jobs=0
    for j in jobs:
        jid=j.get('job_id'); rp=root/(j.get('report_path') or j.get('output_path') or ''); lp=root/j.get('raw_log_path','')
        if j.get('status') not in ['pass','skipped']:
            issues.append({'gate':'CI4','code':'BAD_JOB_STATUS','job_id':jid,'status':j.get('status')})
        if not rp.exists(): issues.append({'gate':'CI5','code':'REPORT_MISSING','job_id':jid,'path':str(rp)}); continue
        recomputed_report_sha=sha(rp)
        if 'report_sha256' in j and recomputed_report_sha!=j.get('report_sha256'):
            issues.append({'gate':'CI5','code':'REPORT_HASH_MISMATCH','job_id':jid,'field':'report_sha256'})
        if 'output_sha256' in j and recomputed_report_sha!=j.get('output_sha256'):
            issues.append({'gate':'CI5','code':'REPORT_HASH_MISMATCH','job_id':jid,'field':'output_sha256'})
        if not lp.exists(): issues.append({'gate':'CI6','code':'RAW_LOG_MISSING','job_id':jid,'path':str(lp)}); continue
        if sha(lp)!=j.get('raw_log_sha256'): issues.append({'gate':'CI6','code':'RAW_LOG_HASH_MISMATCH','job_id':jid})
        try:
            if rp.suffix=='.json':
                rep=json.loads(rp.read_text()); cls=j.get('job_class')
                if cls in ['zero_replay','freeze_replay','local_algebra_kernel','emlgr_api_smoke','external_ci_record_validator'] and rep.get('review_pass') is not True:
                    issues.append({'gate':'CI7','code':'REPORT_REVIEW_NOT_PASS','job_id':jid})
                if cls=='proof_assistant_probe' and (rep.get('compile_claimed') or rep.get('compiled_pass')) and not real:
                    issues.append({'gate':'CI8','code':'DRY_RUN_FALSE_COMPILE_CLAIM','job_id':jid})
        except Exception as e:
            warnings.append({'gate':'CI7','code':'REPORT_READ_WARNING','job_id':jid,'error':repr(e)})
        ok_jobs+=1
    if len(jobs)<5: issues.append({'gate':'CI4','code':'TOO_FEW_JOBS','jobs_checked':len(jobs)})
    required={'zero_replay_v1_1_local','freeze_replay_v1_0_inherited','emlgr_api_unittest_local','local_algebra_kernel_witness','formal_seed_tool_probe'}
    observed={j.get('job_id') for j in jobs}
    missing=sorted(required-observed)
    if missing: issues.append({'gate':'CI4','code':'REQUIRED_JOBS_MISSING','missing':missing})
    gates={f'CI{i}':True for i in range(1,9)}
    for i in issues: gates[i['gate']]=False
    rep={'title':'External CI dry-run validation v1.1','review_pass':len(issues)==0,'real_external_run':real,'jobs_checked':len(jobs),'jobs_ok':ok_jobs,'gates':gates,'issue_count':len(issues),'warning_count':len(warnings),'issues':issues,'warnings':warnings}
    out=pathlib.Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
    if a.md_out:
        lines=['# External CI dry-run validation v1.1','',f"review_pass: `{rep['review_pass']}`",f"real_external_run: `{rep['real_external_run']}`",f"jobs_checked: `{len(jobs)}`",'', '| gate | pass |','|---|---:|']+[f"| `{k}` | `{v}` |" for k,v in gates.items()]
        if issues:
            lines += ['', '## Issues'] + [f"- `{i.get('gate')}` `{i.get('code')}`" for i in issues]
        pathlib.Path(a.md_out).write_text('\n'.join(lines)+'\n')
    print(json.dumps({'review_pass':rep['review_pass'],'jobs_checked':len(jobs),'issue_count':len(issues)},indent=2))
    return 0 if rep['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
