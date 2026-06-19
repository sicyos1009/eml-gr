from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json, hashlib
def sha_file(p:Path)->str:
 h=hashlib.sha256();
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
 return h.hexdigest()
@dataclass(frozen=True)
class ZeroBundle:
 path: Path
 raw: dict[str,Any]
 @classmethod
 def from_path(cls,p):
  p=Path(p); return cls(p,json.loads(p.read_text()))
 @property
 def claims(self): return list(self.raw.get('certificates',[]))
 def claim_ids(self): return [c.get('claim_id') for c in self.claims]
 def summary(self):
  routes=sum(len(c.get('routes',[])) for c in self.claims); steps=sum(len(r.get('steps',[])) for c in self.claims for r in c.get('routes',[]))
  flrw=next((c for c in self.claims if c.get('claim_id')=='zero.flrw.contracted_bianchi_divG0'),{})
  occ=[m for r in flrw.get('routes',[]) for s in r.get('steps',[]) for m in s.get('occurrence_maps',[])]
  return {'claims':len(self.claims),'claim_ids':self.claim_ids(),'routes':routes,'steps':steps,'flrw_tensor_subleaves':len(flrw.get('tensor_subleaves',[])),'flrw_occurrence_maps':len(occ),'flrw_ast_locators':sum(1 for m in occ if m.get('ast_locator')),'flrw_typed_provenance':sum(1 for m in occ if m.get('typed_provenance')),'flrw_typed_dependency_edges':len(flrw.get('typed_dependency_flow',{}).get('typed_dependency_edges',[])),'sha256':sha_file(self.path)}
