#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,shutil,subprocess
from datetime import datetime, timezone
TOOLS={'lean':['lean','--version'],'lake':['lake','--version'],'coqc':['coqc','--version'],'rocq':['rocq','--version']}
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); ap.add_argument('--md-out'); a=ap.parse_args(); tools={}
 for name,cmd in TOOLS.items():
  path=shutil.which(cmd[0]); rec={'found':bool(path),'executable':path,'version_stdout':None,'version_stderr':None,'version_returncode':None}
  if path:
   try:
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=15); rec.update({'version_stdout':p.stdout.strip(),'version_stderr':p.stderr.strip(),'version_returncode':p.returncode})
   except Exception as e: rec.update({'version_stderr':repr(e),'version_returncode':-1})
  tools[name]=rec
 rep={'schema_id':'emlgr.proof_assistant_env_probe.v1_1','created_utc':now(),'real_external_run':False,'compile_attempted':False,'compiled_pass':False,'compile_claimed':False,'any_tool_found':any(r['found'] for r in tools.values()),'tools':tools,'claim_posture':'environment probe only; no compiled theorem claimed','review_pass':True,'issue_count':0,'issues':[]}
 out=pathlib.Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
 if a.md_out:
  lines=['# Proof-assistant environment probe v1.1','','| tool | found | executable |','|---|---:|---|']+[f"| `{k}` | `{v['found']}` | `{v['executable'] or ''}` |" for k,v in tools.items()]+['','No compiled theorem is claimed.']
  pathlib.Path(a.md_out).write_text('\n'.join(lines)+'\n')
 print(json.dumps({'review_pass':True,'compiled_pass':False,'any_tool_found':rep['any_tool_found']},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
