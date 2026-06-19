# Real vs dry-run evidence gates v1.2

| gate | local preflight | hosted real run |
|---|---:|---:|
| `real_external_run` | `false` | `true` |
| `trust_level` | `local_preflight_only` | `hosted_external_ci` |
| `commit_sha` | placeholder allowed | 40-hex required |
| `workflow_run_url` | placeholder allowed | https URL required |
| `raw_log_sha256` | required for local logs | required for hosted logs |
| `compiled_pass_external` | false | true only with passing compile job |
| validator mode | normal | `--require-real` |
