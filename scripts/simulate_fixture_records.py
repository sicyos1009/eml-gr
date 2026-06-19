#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path


def run(cmd, cwd):
    print('+', ' '.join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=True)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ns=ap.parse_args()
    root=Path(ns.root)
    out=root/'examples/generated_records'
    out.mkdir(parents=True, exist_ok=True)
    (root/'examples/lean_fixture_pass.log').write_text('Lean seed fixture: rindler_cancel_int checked.\n', encoding='utf-8')
    (root/'examples/coq_fixture_pass.log').write_text('Coq seed fixture: rindler_cancel_Z checked.\n', encoding='utf-8')
    pkg_sha='0'*64
    run([sys.executable,'scripts/emit_external_ci_result.py','--fixture','--proof-target-id','seed.rindler_cancel.lean.fixture','--tool-name','lean','--tool-version','fixture-lean-4','--command','lean proof_assistant/lean/EMLGRSeedExecutable.lean','--exit-code','0','--log','examples/lean_fixture_pass.log','--target-source','proof_assistant/lean/EMLGRSeedExecutable.lean','--artifact-package-sha256',pkg_sha,'--output',str(out/'lean_pass.json')], root)
    run([sys.executable,'scripts/emit_external_ci_result.py','--fixture','--proof-target-id','seed.rindler_cancel.coq.fixture','--tool-name','coqc','--tool-version','fixture-coq-8.20','--command','coqc proof_assistant/coq/EMLGRSeedExecutable.v','--exit-code','0','--log','examples/coq_fixture_pass.log','--target-source','proof_assistant/coq/EMLGRSeedExecutable.v','--artifact-package-sha256',pkg_sha,'--output',str(out/'coq_pass.json')], root)
    run([sys.executable,'scripts/merge_external_ci_results.py','--records-dir',str(out),'--artifact-package-sha256',pkg_sha,'--output','examples/external_ci_results.example.v1.json'], root)
    run([sys.executable,'scripts/validate_external_ci_results.py','examples/external_ci_results.example.v1.json','--base','.', '--output','outputs/v39_fixture_validation_report.json'], root)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
