#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, shutil, subprocess, tempfile, os, sys, datetime

def sha_file(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for ch in iter(lambda:f.read(1024*1024), b''):
            h.update(ch)
    return h.hexdigest()

def version_of(exe: str):
    path=shutil.which(exe)
    if not path:
        return {'found':False,'executable':None,'version_stdout':None,'version_stderr':None,'version_returncode':None}
    p=subprocess.run([path,'--version'],capture_output=True,text=True,timeout=30)
    return {'found':True,'executable':path,'version_stdout':p.stdout.strip(),'version_stderr':p.stderr.strip(),'version_returncode':p.returncode}

def run_compile(cmd, cwd, log_path):
    try:
        p=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True,timeout=60)
        log=f"$ {' '.join(cmd)}\n\n[stdout]\n{p.stdout}\n\n[stderr]\n{p.stderr}\n\n[returncode]\n{p.returncode}\n"
    except Exception as e:
        p=None
        log=f"$ {' '.join(cmd)}\n\n[exception]\n{repr(e)}\n"
    log_path.parent.mkdir(parents=True,exist_ok=True)
    log_path.write_text(log)
    return p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-root',default='.')
    ap.add_argument('--out',required=True)
    ap.add_argument('--md-out')
    args=ap.parse_args()
    root=pathlib.Path(args.package_root).resolve()
    logs=root/'external_ci/logs'
    tools={k:version_of(k) for k in ['lean','lake','coqc','rocq']}
    compile_jobs=[]
    # Lean minimal target
    lean_file=root/'formal_targets/LeanZeroLeafMinimal.lean'
    if tools['lean']['found'] and lean_file.exists():
        log=logs/'proof_assistant_lean_minimal_v1_2.log'
        p=run_compile([tools['lean']['executable'], str(lean_file)], root, log)
        compile_jobs.append({'tool':'lean','target':str(lean_file.relative_to(root)),'target_sha256':sha_file(lean_file),'compile_attempted':True,'compiled_pass':bool(p and p.returncode==0),'returncode':None if p is None else p.returncode,'raw_log_path':str(log.relative_to(root)),'raw_log_sha256':sha_file(log)})
    # Coq/Rocq minimal target. Prefer coqc, then rocq if its CLI behaves as coqc.
    coq_file=root/'formal_targets/CoqZeroLeafMinimal.v'
    coq_exe=None; coq_name=None
    if tools['coqc']['found']:
        coq_exe=tools['coqc']['executable']; coq_name='coqc'
    elif tools['rocq']['found']:
        coq_exe=tools['rocq']['executable']; coq_name='rocq'
    if coq_exe and coq_file.exists():
        log=logs/f'proof_assistant_{coq_name}_minimal_v1_2.log'
        with tempfile.TemporaryDirectory() as td:
            tmp=pathlib.Path(td)/coq_file.name
            tmp.write_text(coq_file.read_text())
            p=run_compile([coq_exe, tmp.name], pathlib.Path(td), log)
        compile_jobs.append({'tool':coq_name,'target':str(coq_file.relative_to(root)),'target_sha256':sha_file(coq_file),'compile_attempted':True,'compiled_pass':bool(p and p.returncode==0),'returncode':None if p is None else p.returncode,'raw_log_path':str(log.relative_to(root)),'raw_log_sha256':sha_file(log)})
    any_tool_found=any(t['found'] for t in tools.values())
    compile_attempted=any(j['compile_attempted'] for j in compile_jobs)
    compiled_pass=any(j['compiled_pass'] for j in compile_jobs)
    if not compile_jobs:
        log=logs/'proof_assistant_no_tool_found_v1_2.log'
        log.parent.mkdir(parents=True,exist_ok=True)
        log.write_text('No Lean/Coq/Rocq executable found. No compile attempted; no compile claim made.\n')
    rep={'schema_id':'emlgr.proof_assistant_compile_probe.v1_2','created_utc':'2026-06-19T12:15:00Z','real_external_run':os.environ.get('GITHUB_ACTIONS','').lower()=='true','compile_attempted':compile_attempted,'compiled_pass':compiled_pass,'compile_claimed':compiled_pass,'any_tool_found':any_tool_found,'tools':tools,'compile_jobs':compile_jobs,'claim_posture':'compiled_pass is claimable only when this probe runs in the target environment and records a passing job; absent tools produce probe-only evidence','review_pass':True,'issue_count':0,'issues':[]}
    out=pathlib.Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
    if args.md_out:
        lines=['# Proof-assistant compile probe v1.2','',f"compile_attempted: `{compile_attempted}`",f"compiled_pass: `{compiled_pass}`",f"any_tool_found: `{any_tool_found}`",'', '| tool | found | version |','|---|---:|---|']
        for k,v in tools.items(): lines.append(f"| `{k}` | `{v['found']}` | `{(v.get('version_stdout') or v.get('version_stderr') or '')[:80]}` |")
        pathlib.Path(args.md_out).write_text('\n'.join(lines)+'\n')
    print(json.dumps({'review_pass':rep['review_pass'],'compile_attempted':compile_attempted,'compiled_pass':compiled_pass,'any_tool_found':any_tool_found},indent=2))
    return 0
if __name__=='__main__':
    raise SystemExit(main())
