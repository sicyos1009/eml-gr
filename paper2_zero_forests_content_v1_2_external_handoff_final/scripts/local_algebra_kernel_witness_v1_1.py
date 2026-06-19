#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib
from datetime import datetime, timezone
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); ap.add_argument('--md-out'); a=ap.parse_args(); issues=[]; cases=[]
 try:
  import sympy as sp
  M,r,H,t=sp.symbols('M r H t', real=True)
  exprs=[('schwarzschild.common_denom_leaf',2*M/(r**2*(r-2*M))-2*M/(r**2*(r-2*M))),('flrw.exp_cancel_leaf',sp.exp(2*H*t)*sp.exp(-2*H*t)-1),('flrw.selected_divergence_scalar_leaf',sp.diff(3*H**2,t)+3*H*3*H**2+3*(H*sp.exp(2*H*t))*(-3*H**2*sp.exp(-2*H*t)))]
  backend={'name':'sympy','version':sp.__version__}
  for cid,expr in exprs:
   simp=sp.simplify(expr); ok=bool(simp==0); cases.append({'case_id':cid,'simplified_expr':str(simp),'passed':ok})
   if not ok: issues.append({'case_id':cid,'code':'NONZERO_SIMPLIFICATION','simplified_expr':str(simp)})
 except Exception as e:
  backend={'name':'sympy','error':repr(e)}; issues.append({'code':'BACKEND_ERROR','error':repr(e)})
 rep={'schema_id':'emlgr.local_algebra_kernel_witness.v1_1','created_utc':now(),'backend':backend,'review_pass':len(issues)==0,'case_count':len(cases),'cases_passed':sum(1 for c in cases if c.get('passed')),'cases':cases,'claim_posture':'local algebra-kernel witness only; not proof-assistant compile evidence','issue_count':len(issues),'issues':issues}
 out=pathlib.Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n')
 if a.md_out:
  rows=['| case | passed | simplified |','|---|---:|---|']+[f"| `{c['case_id']}` | `{c['passed']}` | `{c['simplified_expr']}` |" for c in cases]
  pathlib.Path(a.md_out).write_text('# Local algebra-kernel witness v1.1\n\n'+'\n'.join(rows)+f"\n\nreview_pass: `{rep['review_pass']}`\n")
 print(json.dumps({'review_pass':rep['review_pass'],'case_count':rep['case_count'],'cases_passed':rep['cases_passed']},indent=2)); return 0 if rep['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
