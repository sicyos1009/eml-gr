#!/usr/bin/env python3
"""Thin wrapper around zero_replay_checker_v0_5_strict.py focused on RC9 tensor-subleaf reports."""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('z05', here / 'zero_replay_checker_v0_5_strict.py')
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    bundle = json.loads(Path(args.bundle).read_text(encoding='utf-8'))
    rep = mod.replay_bundle(bundle)
    out = {
        'review_pass': rep['gates'].get('RC9', False),
        'gate': 'RC9',
        'tensor_subleaf_count': rep['counts'].get('tensor_subleaves', 0),
        'tensor_subleaf_reports': rep.get('tensor_subleaf_reports', []),
        'rc9_issues': [x for x in rep.get('issues', []) if x.get('gate') == 'RC9'],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'review_pass': out['review_pass'], 'tensor_subleaf_count': out['tensor_subleaf_count'], 'rc9_issue_count': len(out['rc9_issues'])}, indent=2, ensure_ascii=False))
    return 0 if out['review_pass'] else 1
if __name__ == '__main__':
    raise SystemExit(main())
