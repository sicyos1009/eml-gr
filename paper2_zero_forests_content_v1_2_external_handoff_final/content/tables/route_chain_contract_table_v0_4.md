# route_chain_contract_table_v0_4

| Gate | Check | Catches |
|---|---|---|
| RC1 | initial expression equivalent to normalized lhs | normalized lhs change, route initial disconnect |
| RC2 | adjacent after/before textual chain | step-order reversal, route disconnect |
| RC3 | last output equals final and final is zero | nonzero final, last-output mismatch |
| RC4 | raw and normalized hashes recompute | raw/normalized hash mutation |
| RC5 | rule registry and scalar replay | unregistered rule, rule-class mismatch, nonzero step |
| RC6 | required rule classes cover route classes | normalized class deletion |
| RC7 | tensor steps remain declared | tensor boundary relabel |
| RC8 | domain refs and side conditions hold | domain ref deletion, domain weakening |
