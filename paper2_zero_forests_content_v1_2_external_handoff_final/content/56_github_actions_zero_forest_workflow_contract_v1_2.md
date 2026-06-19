# GitHub Actions zero-forest workflow contract v1.2

The workflow template is intentionally narrow. It runs the same replay, tamper, local algebra, API smoke, and proof-assistant probe commands that the local package can run, then builds an external-CI record from runner environment variables.

## Expected hosted outputs

```text
external_ci/external_ci_results.v1_2.github_actions.json
outputs/external_ci_validation_v1_2_github_actions.json
outputs/proof_assistant_compile_probe_v1_2.json
outputs/replay_report_v1_2_external_handoff.json
outputs/tamper_suite_v1_2_external_handoff_report.json
```

## Acceptance rule

The hosted record is accepted only if the v1.2 validator passes in `--require-real` mode. A local package can pass preflight without satisfying `--require-real`.

## Workflow pinning note

The included YAML is a handoff template. Before publishing a repository, pin or review any external actions according to the repository security policy.
