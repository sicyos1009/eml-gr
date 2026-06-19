#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, shlex, subprocess
from pathlib import Path
from _common import SCHEMA_VERSION, sha256_file, result_hash, write_json


def detect_tool_version(tool_name: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    cmd = {
        'lean': ['lean', '--version'],
        'lake': ['lake', '--version'],
        'coqc': ['coqc', '--version'],
        'rocq': ['rocq', '--version'],
        'python': ['python', '--version'],
    }.get(tool_name, [tool_name, '--version'])
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        return (out.stdout or '').strip().split('\n')[0] or 'unknown'
    except Exception:
        return 'unavailable'


def provenance_from_env(force_fixture: bool = False) -> dict:
    if os.environ.get('GITHUB_ACTIONS') == 'true' and not force_fixture:
        server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
        repo = os.environ.get('GITHUB_REPOSITORY')
        run_id = os.environ.get('GITHUB_RUN_ID')
        run_url = f"{server}/{repo}/actions/runs/{run_id}" if repo and run_id else None
        return {
            'kind': 'external_ci',
            'real_external_run': True,
            'run_url': run_url,
            'commit_sha': os.environ.get('GITHUB_SHA', ''),
            'run_id': run_id,
            'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
            'repository': repo,
            'ref_name': os.environ.get('GITHUB_REF_NAME'),
            'actor': os.environ.get('GITHUB_ACTOR'),
        }
    return {
        'kind': 'local_fixture' if force_fixture else 'local_simulation',
        'real_external_run': False,
        'run_url': None,
        'commit_sha': 'fixture-not-a-real-commit',
        'run_id': None,
        'run_attempt': None,
        'repository': None,
        'ref_name': None,
        'actor': None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--proof-target-id', required=True)
    ap.add_argument('--tool-name', required=True)
    ap.add_argument('--tool-version')
    ap.add_argument('--command', required=True, help='Command line as executed, shell-like string or JSON argv not required.')
    ap.add_argument('--exit-code', required=True, type=int)
    ap.add_argument('--log', required=True)
    ap.add_argument('--target-source', required=True)
    ap.add_argument('--artifact-package-sha256', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--status', choices=['compiled_pass','compiled_fail','skipped'])
    ap.add_argument('--skip-reason')
    ap.add_argument('--fixture', action='store_true')
    ns = ap.parse_args()

    log = Path(ns.log)
    source = Path(ns.target_source)
    if not log.exists():
        raise SystemExit(f'log not found: {log}')
    if not source.exists():
        raise SystemExit(f'target source not found: {source}')

    if ns.status:
        status = ns.status
    else:
        status = 'compiled_pass' if ns.exit_code == 0 else 'compiled_fail'
    if status == 'compiled_pass' and ns.exit_code != 0:
        raise SystemExit('compiled_pass requires exit code 0')
    if status == 'compiled_fail' and ns.exit_code == 0:
        raise SystemExit('compiled_fail requires nonzero exit code')
    if status == 'skipped' and not ns.skip_reason:
        raise SystemExit('skipped status requires --skip-reason')

    argv = shlex.split(ns.command)
    record = {
        'schema_version': SCHEMA_VERSION,
        'proof_target_id': ns.proof_target_id,
        'status': status,
        'skip_reason': ns.skip_reason if status == 'skipped' else None,
        'tool': {'name': ns.tool_name, 'version': detect_tool_version(ns.tool_name, ns.tool_version)},
        'command': {'argv': argv, 'exit_code': ns.exit_code},
        'raw_log': {'path': str(log), 'sha256': sha256_file(log)},
        'target_source_sha256': sha256_file(source),
        'artifact_package_sha256': ns.artifact_package_sha256,
        'provenance': provenance_from_env(force_fixture=ns.fixture),
    }
    record['result_hash'] = result_hash(record)
    write_json(Path(ns.output), record)
    print(f"wrote {ns.output} status={status} result_hash={record['result_hash']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
