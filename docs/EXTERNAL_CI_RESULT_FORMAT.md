# External CI result record v1.0.0

A proof-assistant compilation result is stored as a versioned, hash-backed record. The record is not just a log: it contains tool identity, command identity, source hash, log hash, package hash, provenance, and a canonical `result_hash`.

Minimal fields:

```json
{
  "schema_version": "eml-gr-external-ci-result/1.0.0",
  "proof_target_id": "seed.rindler_cancel.lean",
  "status": "compiled_pass",
  "tool": {"name": "lean", "version": "..."},
  "command": {"argv": ["lean", "proof_assistant/lean/EMLGRSeedExecutable.lean"], "exit_code": 0},
  "raw_log": {"path": "outputs/lean.log", "sha256": "..."},
  "target_source_sha256": "...",
  "artifact_package_sha256": "...",
  "provenance": {"kind": "external_ci", "real_external_run": true, "run_url": "...", "commit_sha": "..."},
  "result_hash": "..."
}
```

The validator recomputes `raw_log.sha256`, `target_source_sha256`, and `result_hash`, and checks that real external runs have a non-null CI URL and a real commit SHA.
