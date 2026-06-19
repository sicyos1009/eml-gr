#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from _common import SCHEMA_VERSION, sha256_file, result_hash, is_hex_sha, read_json, write_json


def validate_record(record: dict, base: Path) -> tuple[bool, list[str]]:
    errors = []
    required = ['schema_version','proof_target_id','status','tool','command','raw_log','target_source_sha256','artifact_package_sha256','provenance','result_hash']
    for k in required:
        if k not in record:
            errors.append(f'missing {k}')
    if errors:
        return False, errors
    if record['schema_version'] != SCHEMA_VERSION:
        errors.append('wrong schema_version')
    if record['status'] not in ['compiled_pass','compiled_fail','skipped']:
        errors.append('bad status')
    exit_code = record['command'].get('exit_code')
    if record['status'] == 'compiled_pass' and exit_code != 0:
        errors.append('compiled_pass must have exit_code 0')
    if record['status'] == 'compiled_fail' and exit_code == 0:
        errors.append('compiled_fail must have nonzero exit_code')
    if record['status'] == 'skipped' and not record.get('skip_reason'):
        errors.append('skipped must have skip_reason')
    log_path = base / record['raw_log'].get('path','')
    if not log_path.exists():
        # also allow absolute/local path as emitted from CI workspace
        log_path = Path(record['raw_log'].get('path',''))
    if not log_path.exists():
        errors.append('raw log missing')
    else:
        actual = sha256_file(log_path)
        if actual != record['raw_log'].get('sha256'):
            errors.append('raw log hash mismatch')
    if not is_hex_sha(record['target_source_sha256']):
        errors.append('target_source_sha256 malformed')
    if not is_hex_sha(record['artifact_package_sha256']):
        errors.append('artifact_package_sha256 malformed')
    prov = record['provenance']
    if prov.get('real_external_run'):
        if prov.get('kind') != 'external_ci':
            errors.append('real run must have kind external_ci')
        if not prov.get('run_url'):
            errors.append('real external run missing run_url')
        if prov.get('commit_sha') in [None, '', 'fixture-not-a-real-commit']:
            errors.append('real external run missing real commit_sha')
    expected = result_hash(record)
    if expected != record['result_hash']:
        errors.append('result_hash mismatch')
    return not errors, errors


def validate_bundle(bundle: dict, base: Path) -> dict:
    errors = []
    records = bundle.get('records', [])
    if not isinstance(records, list):
        errors.append('records is not a list')
        records = []
    per = []
    counts = {'compiled_pass':0,'compiled_fail':0,'skipped':0}
    real_external = 0
    for i, rec in enumerate(records):
        ok, rec_errors = validate_record(rec, base)
        per.append({'index': i, 'proof_target_id': rec.get('proof_target_id'), 'ok': ok, 'errors': rec_errors})
        if rec.get('status') in counts:
            counts[rec['status']] += 1
        if rec.get('provenance',{}).get('real_external_run'):
            real_external += 1
    summary = bundle.get('summary', {})
    if summary:
        if summary.get('record_count') != len(records):
            errors.append('summary record_count mismatch')
    bundle_no_hash = dict(bundle)
    expected_bundle_hash = None
    if 'bundle_hash' in bundle_no_hash:
        import hashlib
        bundle_no_hash.pop('bundle_hash', None)
        expected_bundle_hash = hashlib.sha256(json.dumps(bundle_no_hash, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()[:16]
        if bundle.get('bundle_hash') != expected_bundle_hash:
            errors.append('bundle_hash mismatch')
    return {
        'record_count': len(records),
        'counts': counts,
        'real_external_runs_count': real_external,
        'record_results': per,
        'bundle_hash_expected': expected_bundle_hash,
        'errors': errors,
        'review_pass': not errors and all(x['ok'] for x in per),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('bundle')
    ap.add_argument('--base', default='.')
    ap.add_argument('--output')
    ns = ap.parse_args()
    bundle_path = Path(ns.bundle)
    report = validate_bundle(read_json(bundle_path), Path(ns.base))
    if ns.output:
        write_json(Path(ns.output), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['review_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
