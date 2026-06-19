# `emlgr` certificate API integration contract v1.1

v1.1 includes a small `emlgr_integration/` skeleton with:

```python
from emlgr.certificates import ZeroBundle
from emlgr.validation import validate_zero_bundle
```

The smoke test verifies that the current bundle exposes the frozen counts: 4 claims, 8 routes, 6 FLRW tensor subleaves, and 10 typed dependency edges.
