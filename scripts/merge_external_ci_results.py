#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from _common import read_json, write_json, canonical_json


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--records-dir', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--artifact-package-sha256', required=True)
    ns = ap.parse_args()
    recs = []
    for path in sorted(Path(ns.records_dir).glob('*.json')):
        recs.append(read_json(path))
    counts = {'compiled_pass':0,'compiled_fail':0,'skipped':0}
    real = 0
    for r in recs:
        counts[r.get('status')] = counts.get(r.get('status'),0)+1
        if r.get('provenance',{}).get('real_external_run'):
            real += 1
    bundle = {
        'schema_version': 'eml-gr-external-ci-result-bundle/1.0.0',
        'artifact_package_sha256': ns.artifact_package_sha256,
        'summary': {
            'record_count': len(recs),
            'counts': counts,
            'real_external_runs_count': real,
            'fixture_or_simulated_runs_count': len(recs)-real,
        },
        'records': recs,
    }
    bundle['bundle_hash'] = hashlib.sha256(canonical_json(bundle).encode()).hexdigest()[:16]
    write_json(Path(ns.output), bundle)
    print(f"wrote {ns.output} records={len(recs)} bundle_hash={bundle['bundle_hash']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
