# EML-GR v0.39 — GitHub Actions release template

v0.39 turns the v0.37/v0.38 proof-assistant harness into a repository-ready GitHub Actions release template.

## Goal

The goal is not to claim that Lean or Rocq/Coq was compiled in the current sandbox. The goal is to provide workflows and scripts so that an external repository run can compile the seed proof target, emit a normalized external-CI record, validate hashes/provenance, and upload an audit bundle.

## Included workflows

- `.github/workflows/proof-assistant-external-ci.yml`
  - builds a source release package and computes its SHA256
  - runs a Lean seed job
  - runs a Rocq/Coq seed job
  - emits external-CI JSON records from proof-assistant logs
  - merges and validates records
  - uploads `external-ci-results-v1`

- `.github/workflows/release-artifact-audit.yml`
  - runs the local template audit
  - builds a release package
  - uploads the audit bundle

## Included scripts

- `scripts/emit_external_ci_result.py`
- `scripts/merge_external_ci_results.py`
- `scripts/validate_external_ci_results.py`
- `scripts/package_release_artifact.py`
- `scripts/simulate_fixture_records.py`
- `scripts/run_tamper_tests.py`
- `scripts/review_v39_template.py`

## Normalized result fields

Each proof-assistant job emits a record with:

```text
proof_target_id
tool.name
tool.version
command.argv
command.exit_code
raw_log.sha256
target_source_sha256
artifact_package_sha256
provenance
status
result_hash
```

## Local review status

The local review does fixture-based validation only. It verifies schema/hash/tamper behavior but does not assert a real external proof-assistant run.

```text
REVIEW_STATUS: PASS
```

## Main limitation

A record is considered real proof-assistant evidence only if:

```text
provenance.kind = external_ci
provenance.real_external_run = true
provenance.run_url != null
provenance.commit_sha != fixture-not-a-real-commit
```
