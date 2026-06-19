# v1.1 evidence-depth scope

v1.1 does not add another zero-forest object layer. The v1.0 frozen layers remain canonical: strict replay, tensor subleaves, occurrence maps, AST locators, typed provenance, typed dependency flow, and freeze gates.

v1.1 adds evidence-depth channels around that freeze:

| Channel | v1.1 status | Claim strength |
|---|---|---|
| Core replay | local executable pass | Level-B+ |
| Freeze inheritance | local executable pass | Level-B+ |
| External CI | dry-run provenance record | plumbing evidence |
| Proof assistant | environment probe only | no compile claim |
| Local algebra kernel | selected algebra leaves pass | implementation evidence |
| `emlgr` API | skeleton + smoke pass | integration contract |

Non-goals: real GitHub Actions evidence, Lean/Coq/Rocq compile evidence, full tensor CAS verification, full componentwise Bianchi theorem, and universal zero-decision.
