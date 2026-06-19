# Reproducing v0.39 in a GitHub repository

1. Copy the package contents into a clean repository.
2. Commit all files.
3. Push to GitHub.
4. Open the Actions tab and run `Proof-assistant external CI ingestion`.
5. Download the `external-ci-results-v1` artifact.
6. Run the validator locally if desired:

```bash
python scripts/validate_external_ci_results.py path/to/external_ci_results.v1.json
```

For a release-style package, run the `Release artifact audit` workflow. It creates a release zip, computes its SHA256, runs local template checks, and uploads an audit bundle.

## Expected status fields

`compiled_pass` means the proof-assistant command exited with code 0.
`compiled_fail` means the command was run but exited nonzero.
`skipped` means no proof-assistant executable was available or the job was explicitly skipped.

## Current sandbox status

The v0.39 package was built in a sandbox without Lean/Rocq/Coq/Docker execution. The included local review uses fixtures and verifies schema/hash/tamper behavior only.
