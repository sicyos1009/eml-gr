# External handoff readiness matrix v1.2

readiness_pass: `True`

real_external_run_available: `False`

proof_assistant_compiled_pass_available: `False`

| item | status | evidence |
|---|---|---|
| canonical v1.2 bundle | ready | `evidence/examples/zero_bundle_v1_2.v1_2_external_handoff.json` |
| local preflight external record | pass | `external_ci/external_ci_results.v1_2.local_preflight.json` |
| strict real validator | ready; rejects local preflight in --require-real mode | `outputs/external_ci_validation_v1_2_require_real_expected_fail.json` |
| hosted workflow template | ready | `.github/workflows/paper2_zero_forest_external_ci.yml` |
| proof assistant compile evidence | not claimed in packaged local preflight | `outputs/proof_assistant_compile_probe_v1_2.json` |
| tamper suite | pass | `outputs/tamper_suite_v1_2_external_handoff_report.json` |
