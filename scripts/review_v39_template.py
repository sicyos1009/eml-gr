#!/usr/bin/env python3
from __future__ import annotations
import copy, json, subprocess, sys, zipfile, hashlib, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_json, write_json
from validate_external_ci_results import validate_bundle

REQUIRED = [
    'README.md','REPRODUCE_GITHUB_ACTIONS.md',
    '.github/workflows/proof-assistant-external-ci.yml',
    '.github/workflows/release-artifact-audit.yml',
    'scripts/emit_external_ci_result.py','scripts/merge_external_ci_results.py','scripts/validate_external_ci_results.py',
    'proof_assistant/lean/EMLGRSeedExecutable.lean','proof_assistant/coq/EMLGRSeedExecutable.v',
    'schemas/external_ci_result.schema.v1_0_0.json'
]

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def make_zip(root: Path, out: Path):
    out.parent.mkdir(exist_ok=True, parents=True)
    files=[]
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if not p.is_file(): continue
        if '.git' in rel.parts or '__pycache__' in rel.parts: continue
        if p.suffix in ['.pyc'] or p.name.endswith('.zip'): continue
        if str(rel).startswith('outputs/') and p.name.endswith('.zip'): continue
        if p.resolve()==out.resolve(): continue
        files.append(p)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files: z.write(p,p.relative_to(root).as_posix())
    return sha256_file(out)

def main() -> int:
    root=Path('.').resolve(); outputs=root/'outputs'; outputs.mkdir(exist_ok=True)
    checks={}
    checks['required_files_exist']=all((root/p).exists() for p in REQUIRED)
    proof_wf=(root/'.github/workflows/proof-assistant-external-ci.yml').read_text(encoding='utf-8')
    release_wf=(root/'.github/workflows/release-artifact-audit.yml').read_text(encoding='utf-8')
    wf=proof_wf+release_wf
    checks['workflow_uses_upload_artifact_v4']='actions/upload-artifact@v4' in wf
    checks['workflow_uses_download_artifact_v4']='actions/download-artifact@v4' in wf
    checks['workflow_has_lean_job']='lean-seed' in proof_wf and 'leanprover/lean-action@v1' in proof_wf
    checks['workflow_has_rocq_job']='rocq-coq-seed' in proof_wf and 'docker-coq-action@v1' in proof_wf
    checks['workflow_emits_external_ci']='emit_external_ci_result.py' in proof_wf
    checks['workflow_merges_results']='merge_external_ci_results.py' in proof_wf
    checks['workflow_validates_results']='validate_external_ci_results.py' in proof_wf
    # ensure fixture bundle exists by running a small generator once
    if not (root/'examples/external_ci_results.example.v1.json').exists():
        sim=subprocess.run([sys.executable,'scripts/simulate_fixture_records.py','--root','.'], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
        checks['fixture_simulation_rc0']=sim.returncode==0
    else:
        checks['fixture_simulation_rc0']=True
    bundle_path=root/'examples/external_ci_results.example.v1.json'
    checks['fixture_bundle_exists']=bundle_path.exists()
    bundle=read_json(bundle_path)
    checks['fixture_bundle_record_count_2']=len(bundle.get('records',[]))==2
    checks['fixture_bundle_no_real_external_runs']=bundle.get('summary',{}).get('real_external_runs_count')==0
    val=validate_bundle(bundle, root)
    checks['fixture_bundle_valid']=val.get('review_pass') is True
    # In-process tamper tests
    tamper=[]
    def test_case(name, modified, should_pass):
        rep=validate_bundle(modified, root)
        tamper.append({'case':name,'observed_pass':rep['review_pass'],'expected_pass':should_pass,'passed':rep['review_pass']==should_pass})
    test_case('baseline_should_pass', copy.deepcopy(bundle), True)
    b=copy.deepcopy(bundle); b['records'][0]['result_hash']='f'*16; test_case('result_hash_mismatch_should_fail', b, False)
    b=copy.deepcopy(bundle); b['records'][0]['command']['exit_code']=1; test_case('status_exit_mismatch_should_fail', b, False)
    b=copy.deepcopy(bundle); b['records'][0]['provenance']['real_external_run']=True; b['records'][0]['provenance']['kind']='external_ci'; b['records'][0]['provenance']['run_url']=None; b['records'][0]['provenance']['commit_sha']='abc123'; test_case('real_run_without_url_should_fail', b, False)
    b=copy.deepcopy(bundle); b['records'][0]['artifact_package_sha256']='not-a-sha'; test_case('artifact_sha_malformed_should_fail', b, False)
    checks['tamper_review_pass']=all(x['passed'] for x in tamper)
    write_json(outputs/'v39_tamper_report.json', {'cases':tamper,'review_pass':checks['tamper_review_pass']})
    pkg=outputs/'v39_release_template_check.zip'; sha=make_zip(root,pkg); (outputs/'v39_release_template_check.sha256').write_text(sha+'\n', encoding='utf-8')
    checks['package_zip_exists']=pkg.exists()
    checks['package_sha_exists']=len(sha)==64
    checks['honesty_note_present']='does not claim' in (root/'README.md').read_text(encoding='utf-8')
    review_pass=all(checks.values())
    report={'checks':checks,'tamper_cases':tamper,'fixture_validation':val,'review_pass':review_pass}
    write_json(outputs/'v39_template_review_report.json', report)
    text=json.dumps(report, indent=2, sort_keys=True)+'\nREVIEW_STATUS: '+('PASS' if review_pass else 'FAIL')+'\n'
    (outputs/'v39_template_review_output.txt').write_text(text, encoding='utf-8')
    print(text)
    return 0 if review_pass else 1
if __name__=='__main__':
    raise SystemExit(main())
