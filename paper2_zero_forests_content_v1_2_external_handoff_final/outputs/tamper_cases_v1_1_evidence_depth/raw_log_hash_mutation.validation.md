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
| `CI5` | `True` |
| `CI6` | `False` |
| `CI7` | `True` |
| `CI8` | `True` |

## Issues
- `CI6` `RAW_LOG_HASH_MISMATCH`
