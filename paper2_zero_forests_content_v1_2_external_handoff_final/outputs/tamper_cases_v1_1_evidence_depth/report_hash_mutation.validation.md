# External CI dry-run validation v1.1

review_pass: `False`
real_external_run: `False`
jobs_checked: `5`

| gate | pass |
|---|---:|
| `CI1` | `True` |
| `CI2` | `True` |
| `CI3` | `True` |
| `CI4` | `True` |
| `CI5` | `False` |
| `CI6` | `True` |
| `CI7` | `True` |
| `CI8` | `True` |

## Issues
- `CI5` `REPORT_HASH_MISMATCH`
