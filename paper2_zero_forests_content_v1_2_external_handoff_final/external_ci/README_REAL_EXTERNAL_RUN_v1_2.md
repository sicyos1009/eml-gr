# Real external run handoff v1.2

From a repository root that contains this package directory, run the included workflow or invoke:

```bash
cd paper2_zero_forests_content_v1_2_external_handoff_final
python scripts/run_ci_payload_v1_2.py --package-root .
python scripts/external_ci_record_builder_v1_2.py --package-root . --mode github_actions --out external_ci/external_ci_results.v1_2.github_actions.json
python scripts/external_ci_record_validator_v1_2.py --package-root .   --record external_ci/external_ci_results.v1_2.github_actions.json   --out outputs/external_ci_validation_v1_2_github_actions.json   --md-out outputs/external_ci_validation_v1_2_github_actions.md   --require-real
```

The packaged local record is not a substitute for this. It is a preflight only.
