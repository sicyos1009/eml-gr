# Real external evidence intake contract v1.2

A real external record is not a label; it is a provenance object.

## Required fields for `real_external_run=true`

```text
provider: github-actions or another hosted CI provider
trust_level: hosted_external_ci
repository: non-placeholder repository identifier
commit_sha: 40 hexadecimal characters
workflow_run_url: https URL for the run
runner_image: hosted runner image or container digest
tool_versions: Python plus optional Lean/Coq/Rocq versions
jobs: hash-checked job records
limitations: non-empty list
```

## Required job classes

```text
zero_replay
tamper_suite
local_algebra_kernel
emlgr_api_smoke
proof_assistant_compile_probe
```

A proof-assistant compile pass is optional at the record level, but if `compiled_pass_external=true` is claimed, at least one job with class `proof_assistant_compile` must pass with a raw log hash and tool version.

## Local preflight rule

A local run may validate the scripts and checksums, but it must remain:

```text
real_external_run: false
trust_level: local_preflight_only
compiled_pass_external: false
```
