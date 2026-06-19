# External CI job matrix v1.2

| job_id | job_class | local preflight | hosted expected | claim role |
|---|---|---:|---:|---|
| `zero_replay_v1_2` | `zero_replay` | pass | pass | replay current canonical bundle |
| `tamper_suite_v1_2` | `tamper_suite` | pass | pass | reject malformed external claims |
| `local_algebra_kernel_witness` | `local_algebra_kernel` | pass | pass | seed algebra leaf sanity check |
| `emlgr_api_smoke` | `emlgr_api_smoke` | pass | pass | certificate API contract smoke |
| `proof_assistant_compile_probe` | `proof_assistant_compile_probe` | pass-or-skip | pass-or-skip | environment/compile probe without overclaim |
