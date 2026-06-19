#!/usr/bin/env python3
from __future__ import annotations
import argparse,pathlib,sys,json
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--package-root',default='.'); ap.add_argument('--bundle',default='evidence/examples/zero_bundle_v1_2.current.json'); ap.add_argument('--out',required=True); ap.add_argument('--md-out'); a=ap.parse_args(); root=pathlib.Path(a.package_root).resolve(); sys.path.insert(0,str(root/'emlgr_integration'))
 from emlgr.certificates import ZeroBundle
 from emlgr.validation import validate_zero_bundle
 b=ZeroBundle.from_path(root/a.bundle); rep=validate_zero_bundle(b); out=pathlib.Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps({'schema_id':'emlgr.api_contract_smoke.v1_1',**rep},indent=2,ensure_ascii=False)+'\n')
 if a.md_out:
  s=rep['summary']; pathlib.Path(a.md_out).write_text('# emlgr API smoke v1.1\n\n'+ '\n'.join([f'- {k}: `{v}`' for k,v in s.items() if k!='claim_ids'])+f"\n\nreview_pass: `{rep['review_pass']}`\n")
 print(json.dumps({'review_pass':rep['review_pass'],'issue_count':rep['issue_count']},indent=2)); return 0 if rep['review_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
