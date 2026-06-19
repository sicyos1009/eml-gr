# External-CI ingestion contract v1.1

The v1.1 external-CI record is deliberately a dry-run record:

```text
real_external_run: false
trust_level: dry_run_provenance_only
```

A future record may claim `real_external_run=true` only if repository, commit SHA, workflow URL, runner/tool versions, raw logs, raw-log SHA256, and report SHA256 are all present.

The validator rejects stale raw-log hashes, stale report hashes, bundle-hash drift, false real-run claims, and proof-assistant compile claims in a dry-run record.
