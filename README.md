# EML-GR v0.39 GitHub Actions release template

This package is the v0.39 release/CI template for the EML-GR proof-carrying artifact line.
It is intended to be copied into a GitHub repository. The workflows compile the tiny proof-assistant seed targets, turn Lean/Rocq/Coq logs into normalized external-CI result records, validate the records, and upload the resulting audit bundle.

This package **does not claim** that Lean/Rocq/Coq was compiled in the current sandbox. It provides a repository-ready template and local fixture tests. A real proof-assistant compilation only counts as external evidence when the normalized CI record contains:

```text
provenance.kind = external_ci
provenance.real_external_run = true
provenance.run_url != null
provenance.commit_sha != fixture-not-a-real-commit
```

## Quick local check

```bash
python scripts/review_v39_template.py
```

## Repository CI check

After copying this package into a repository, enable GitHub Actions and run:

```text
.github/workflows/proof-assistant-external-ci.yml
.github/workflows/release-artifact-audit.yml
```

The workflow output of interest is:

```text
external-ci-results-v1
release-audit-bundle
```

## Main contents

```text
.github/workflows/                  GitHub Actions workflow templates
proof_assistant/lean/               Lean seed target
proof_assistant/coq/                Rocq/Coq seed target
schemas/                            external CI result schema
scripts/                            emit/merge/validate/audit scripts
examples/                           local fixture logs and generated example bundle
docs/                               design notes
```
