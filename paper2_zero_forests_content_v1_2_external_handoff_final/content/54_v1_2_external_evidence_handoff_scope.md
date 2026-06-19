# v1.2 external-evidence handoff scope

This package continues Paper2 content development without creating a manuscript. It upgrades the v1.1 evidence-depth kit into a handoff package for real hosted CI and proof-assistant compile evidence.

## In scope

- Hosted-CI record schema and validator.
- GitHub Actions workflow template.
- Local preflight record generation.
- Proof-assistant compile probe for Lean/Coq/Rocq targets.
- Strict rejection of false `real_external_run=true` claims.
- Hash-checked raw logs and output reports.

## Out of scope

- No `paper/` directory.
- No LaTeX manuscript.
- No PDF draft.
- No claimed hosted CI success from this local package.
- No claimed Lean/Coq/Rocq compiled theorem unless the compile wrapper records a passing external run.

## Handoff principle

The v1.2 package is a bridge from content evidence to externally reproducible evidence. It is considered successful when the local preflight passes and the package contains enough deterministic scripts for a hosted runner to produce a stricter record later.
