#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, hashlib, re, sys

def sha_file(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for ch in iter(lambda:f.read(1024*1024), b''):
            h.update(ch)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-root',default='.')
    ap.add_argument('--record',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--md-out')
    ap.add_argument('--require-real',action='store_true')
    args=ap.parse_args()
    root=pathlib.Path(args.package_root).resolve()
    issues=[]; warnings=[]
    try:
        rec=json.loads((root/args.record).read_text())
    except Exception as e:
        rec={}; issues.append({'gate':'XR1','code':'RECORD_READ_ERROR','error':repr(e)})
    if rec.get('schema_id')!='emlgr.external_ci_results.v1_2':
        issues.append({'gate':'XR1','code':'BAD_SCHEMA_ID','observed':rec.get('schema_id')})
    real=bool(rec.get('real_external_run'))
    if args.require_real and not real:
        issues.append({'gate':'XR2','code':'REQUIRE_REAL_BUT_RECORD_IS_LOCAL'})
    if real:
        if rec.get('provider') in [None,'local','local-preflight','local-dry-run']:
            issues.append({'gate':'XR2','code':'BAD_REAL_PROVIDER','provider':rec.get('provider')})
        if rec.get('trust_level')!='hosted_external_ci':
            issues.append({'gate':'XR2','code':'BAD_REAL_TRUST_LEVEL','trust_level':rec.get('trust_level')})
        for k in ['repository','commit_sha','workflow_run_url','runner_image','tool_versions']:
            v=rec.get(k)
            if not v or str(v).startswith('not_applicable') or str(v).startswith('REPLACE'):
                issues.append({'gate':'XR2','code':'MISSING_REAL_RUN_PROVENANCE','field':k,'observed':v})
        if not re.fullmatch(r'[0-9a-fA-F]{40}',str(rec.get('commit_sha',''))):
            issues.append({'gate':'XR2','code':'BAD_COMMIT_SHA','observed':rec.get('commit_sha')})
        if not str(rec.get('workflow_run_url','')).startswith('https://'):
            issues.append({'gate':'XR2','code':'BAD_WORKFLOW_RUN_URL','observed':rec.get('workflow_run_url')})
    else:
        if rec.get('trust_level') not in ['local_preflight_only','dry_run_provenance_only','handoff_template_only']:
            issues.append({'gate':'XR2','code':'BAD_LOCAL_TRUST_LEVEL','observed':rec.get('trust_level')})
        if rec.get('summary',{}).get('compiled_pass_external'):
            issues.append({'gate':'XR8','code':'LOCAL_RECORD_CLAIMS_EXTERNAL_COMPILE'})
    bp=root/rec.get('canonical_bundle_path','') if rec.get('canonical_bundle_path') else None
    if not bp or not bp.exists():
        issues.append({'gate':'XR3','code':'BUNDLE_MISSING','path':rec.get('canonical_bundle_path')})
    else:
        got=sha_file(bp)
        if got!=rec.get('canonical_bundle_sha256'):
            issues.append({'gate':'XR3','code':'BUNDLE_HASH_MISMATCH','reported':rec.get('canonical_bundle_sha256'),'recomputed':got})
    jobs=rec.get('jobs',[])
    if not isinstance(jobs,list):
        jobs=[]; issues.append({'gate':'XR4','code':'JOBS_NOT_LIST'})
    job_ids=set(); classes=set(); pass_compile_jobs=0; ok_jobs=0
    for j in jobs:
        jid=j.get('job_id'); cls=j.get('job_class'); classes.add(cls); job_ids.add(jid)
        if j.get('status') not in ['pass','skipped']:
            issues.append({'gate':'XR4','code':'BAD_JOB_STATUS','job_id':jid,'status':j.get('status')})
        rp=root/(j.get('report_path') or j.get('output_path') or '')
        if not rp.exists():
            issues.append({'gate':'XR5','code':'REPORT_MISSING','job_id':jid,'path':str(rp.relative_to(root) if str(rp).startswith(str(root)) else rp)})
        else:
            got=sha_file(rp)
            if j.get('report_sha256') and got!=j.get('report_sha256'):
                issues.append({'gate':'XR5','code':'REPORT_HASH_MISMATCH','job_id':jid,'field':'report_sha256'})
            if j.get('output_sha256') and got!=j.get('output_sha256'):
                issues.append({'gate':'XR5','code':'OUTPUT_HASH_MISMATCH','job_id':jid})
            if rp.suffix=='.json':
                try:
                    rep=json.loads(rp.read_text())
                    if cls in ['zero_replay','tamper_suite','local_algebra_kernel','emlgr_api_smoke'] and rep.get('review_pass') is not True and rep.get('all_expectations_met') is not True:
                        issues.append({'gate':'XR7','code':'REPORT_NOT_PASS','job_id':jid,'class':cls})
                    if cls in ['proof_assistant_compile','proof_assistant_compile_probe']:
                        if rep.get('compiled_pass') is True:
                            pass_compile_jobs += 1
                        if not real and (rep.get('compiled_pass') or rep.get('compile_claimed')):
                            warnings.append({'gate':'XR8','code':'LOCAL_PROBE_REPORTED_COMPILE_PASS_BUT_RECORD_REMAINS_LOCAL','job_id':jid})
                except Exception as e:
                    warnings.append({'gate':'XR7','code':'REPORT_READ_WARNING','job_id':jid,'error':repr(e)})
        lp=root/j.get('raw_log_path','') if j.get('raw_log_path') else None
        if not lp or not lp.exists():
            issues.append({'gate':'XR6','code':'RAW_LOG_MISSING','job_id':jid,'path':j.get('raw_log_path')})
        else:
            got=sha_file(lp)
            if got!=j.get('raw_log_sha256'):
                issues.append({'gate':'XR6','code':'RAW_LOG_HASH_MISMATCH','job_id':jid})
        ok_jobs += 1
    required={'zero_replay','tamper_suite','local_algebra_kernel','emlgr_api_smoke','proof_assistant_compile_probe'}
    missing=sorted(required-classes)
    if missing:
        issues.append({'gate':'XR4','code':'REQUIRED_JOB_CLASSES_MISSING','missing':missing})
    if len(jobs)<5:
        issues.append({'gate':'XR4','code':'TOO_FEW_JOBS','observed':len(jobs)})
    if rec.get('summary',{}).get('compiled_pass_external') and pass_compile_jobs<1:
        issues.append({'gate':'XR8','code':'COMPILED_PASS_EXTERNAL_WITHOUT_PASSING_COMPILE_JOB'})
    if not rec.get('limitations'):
        issues.append({'gate':'XR9','code':'LIMITATIONS_MISSING'})
    gates={f'XR{i}':True for i in range(1,10)}
    for i in issues:
        gates[i['gate']]=False
    rep={'title':'External CI record validation v1.2','review_pass':len(issues)==0,'require_real':args.require_real,'real_external_run':real,'jobs_checked':len(jobs),'job_classes':sorted(str(c) for c in classes),'jobs_ok_or_checked':ok_jobs,'pass_compile_jobs':pass_compile_jobs,'gates':gates,'issue_count':len(issues),'warning_count':len(warnings),'issues':issues,'warnings':warnings}
    out=pathlib.Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
    if args.md_out:
        lines=['# External CI validation v1.2','',f"review_pass: `{rep['review_pass']}`",f"require_real: `{args.require_real}`",f"real_external_run: `{real}`",f"jobs_checked: `{len(jobs)}`",'', '| gate | pass |','|---|---:|']+[f"| `{k}` | `{v}` |" for k,v in gates.items()]
        if issues:
            lines += ['','## Issues']+[f"- `{i.get('gate')}` `{i.get('code')}`" for i in issues]
        if warnings:
            lines += ['','## Warnings']+[f"- `{w.get('gate')}` `{w.get('code')}`" for w in warnings]
        pathlib.Path(args.md_out).write_text('\n'.join(lines)+'\n')
    print(json.dumps({'review_pass':rep['review_pass'],'real_external_run':real,'require_real':args.require_real,'jobs_checked':len(jobs),'issue_count':len(issues)},indent=2))
    return 0 if rep['review_pass'] else 1
if __name__=='__main__':
    raise SystemExit(main())
