# Replay gate v0.9

v0.9 adds dependency-flow gates `DF1` through `DF10` on top of the v0.8 strict replay gates.

| gate | check | pass |
| --- | --- | --- |
| DF1 | flow/edge object and profile | True |
| DF2 | source/target leaf rule/hash binding | True |
| DF3 | declared dependency consistency | True |
| DF4 | payload field and type declaration consistency | True |
| DF5 | dependency-kind type-flow registry | True |
| DF6 | scope and domain propagation | True |
| DF7 | DAG acyclicity, topological order, root/sink reachability, sink exposes normalized lhs | True |
| DF8 | coverage of declared dependency pairs | True |
| DF9 | edge and flow hash recomputation | True |
| DF10 | typed provenance source closure in typeflow | True |


The baseline replay report is stored at:

```text
outputs/replay_report_v0_9_typeflow.json
outputs/replay_report_v0_9_typeflow.md
```
