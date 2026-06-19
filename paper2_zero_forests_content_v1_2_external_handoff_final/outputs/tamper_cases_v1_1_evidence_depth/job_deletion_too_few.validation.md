# External CI dry-run validation v1.1

review_pass: `False`
real_external_run: `False`
jobs_checked: `4`

| gate | pass |
|---|---:|
| `CI1` | `True` |
| `CI2` | `True` |
| `CI3` | `True` |
| `CI4` | `False` |
| `CI5` | `True` |
| `CI6` | `True` |
| `CI7` | `True` |
| `CI8` | `True` |

## Issues
- `CI4` `TOO_FEW_JOBS`
- `CI4` `REQUIRED_JOBS_MISSING`
