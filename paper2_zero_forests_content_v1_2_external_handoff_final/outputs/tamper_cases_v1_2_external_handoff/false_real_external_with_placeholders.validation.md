# External CI validation v1.2

review_pass: `False`
require_real: `False`
real_external_run: `True`
jobs_checked: `5`

| gate | pass |
|---|---:|
| `XR1` | `True` |
| `XR2` | `False` |
| `XR3` | `True` |
| `XR4` | `True` |
| `XR5` | `True` |
| `XR6` | `True` |
| `XR7` | `True` |
| `XR8` | `True` |
| `XR9` | `True` |

## Issues
- `XR2` `MISSING_REAL_RUN_PROVENANCE`
- `XR2` `MISSING_REAL_RUN_PROVENANCE`
- `XR2` `MISSING_REAL_RUN_PROVENANCE`
- `XR2` `BAD_COMMIT_SHA`
- `XR2` `BAD_WORKFLOW_RUN_URL`
