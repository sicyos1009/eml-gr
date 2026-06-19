# External CI dry-run validation v1.1

review_pass: `False`
real_external_run: `True`
jobs_checked: `5`

| gate | pass |
|---|---:|
| `CI1` | `True` |
| `CI2` | `False` |
| `CI3` | `True` |
| `CI4` | `True` |
| `CI5` | `True` |
| `CI6` | `True` |
| `CI7` | `True` |
| `CI8` | `True` |

## Issues
- `CI2` `MISSING_REAL_RUN_PROVENANCE`
- `CI2` `MISSING_REAL_RUN_PROVENANCE`
- `CI2` `MISSING_REAL_RUN_PROVENANCE`
- `CI2` `BAD_COMMIT_SHA`
