# Tamper expectation matrix

| case_id | expected_gate | seed_replay_pass | content_lint_pass | rationale |
|---|---|---|---|---|
| baseline_untampered | pass | True | True | Original v0.2 seed bundle should pass seed replay and content linter. |
| tamper_raw_hash_literal | fail | False | False | Route-sensitive raw trace hash is changed without matching route material. |
| tamper_normalized_hash_literal | fail | False | False | Route-independent normalized evidence hash is changed. |
| tamper_final_expr_nonzero_no_rehash | fail | False | False | Final expression is nonzero and raw hash also becomes stale. |
| tamper_final_expr_nonzero_rehashed | fail | False | False | Even with fresh raw hash, final zero check must fail. |
| tamper_unregistered_rule_rehashed | fail | False | False | Rule registry integrity should reject unknown rule identifiers. |
| tamper_rule_class_mismatch_rehashed | fail | False | False | Registered rule class and step class disagree. |
| tamper_step_expression_nonzero_rehashed | fail | False | False | A scalar replay step no longer preserves expression equality. |
| tamper_domain_ref_deleted_no_rehash | fail | False | False | Domain side condition deletion makes normalized hash stale and mismatches normalized obligation refs. |
| tamper_domain_ref_deleted_rehashed | content_gap | True | True | Seed replay accepts self-consistent weakened domain refs; semantic domain-policy validation is a next gate. |
| tamper_route_initial_disconnect_rehashed | content_linter_fail | True | False | Individual steps preserve equality, but route no longer starts from an expression equivalent to the normalized obligation. |
| tamper_route_step_order_reversed_rehashed | content_linter_fail | True | False | Step multiset is not enough; route chain order must be checked. |
