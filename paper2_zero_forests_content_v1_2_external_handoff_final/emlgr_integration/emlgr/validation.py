from __future__ import annotations
from pathlib import Path
from .certificates import ZeroBundle
def validate_zero_bundle(bundle: ZeroBundle):
 s=bundle.summary(); exp={'claims':4,'routes':8,'flrw_tensor_subleaves':6,'flrw_typed_dependency_edges':10}; issues=[]
 for k,v in exp.items():
  if s.get(k)!=v: issues.append({'code':'COUNT_MISMATCH','field':k,'expected':v,'observed':s.get(k)})
 return {'review_pass':len(issues)==0,'summary':s,'expected_counts':exp,'issues':issues,'issue_count':len(issues)}
