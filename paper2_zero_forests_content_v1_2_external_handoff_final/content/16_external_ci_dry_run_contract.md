# External CI dry-run contract v0.4-final

This content kit emits a local dry-run record only.  It is shaped so that WP8 can replace it with a real external GitHub Actions record.

```json
{
  "record_schema": "external_ci_results.v1",
  "target": "paper2_zero_forests_content_v0_4_final",
  "real_external_run": false,
  "checker_pass": true,
  "tamper_expectations_met": true,
  "compiled_pass": null,
  "commit_sha": "LOCAL_CONTENT_KIT_NOT_A_REPO",
  "raw_log_sha256": "..."
}
```

Real external evidence must later include:

```text
real_external_run: true
repository URL or release tag
commit SHA
tool version
raw log SHA256
pass/fail/skipped provenance
```
