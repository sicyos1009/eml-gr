| edge_id | dependency_kind | source_subleaf | source_fields | target_subleaf | target_fields | domain_refs | edge_hash |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flrw.tf.e01.metric_to_gamma_trace | metric_to_connection | flrw.metric.scale_factor | a_expr | flrw.connection.gamma_trace_0 | a_dot_over_a_expr, gamma_trace_0_expr | DOM.REAL_BRANCH | e7d66841aa4a9d3c |
| flrw.tf.e02.metric_to_gamma_0ii | metric_to_connection | flrw.metric.scale_factor | a_expr, g_ii | flrw.connection.gamma_0ii | gamma_0ii_expr | DOM.REAL_BRANCH | 1a37ae18bdb8e0e3 |
| flrw.tf.e03.metric_to_G00 | metric_to_einstein_tensor | flrw.metric.scale_factor | a_expr, g_contra_00 | flrw.einstein.G_contra_00 | G_contra_00_expr | DOM.REAL_BRANCH | a69c38c4e7d2b138 |
| flrw.tf.e04.metric_to_Gii | metric_to_einstein_tensor | flrw.metric.scale_factor | a_expr, g_contra_ii | flrw.einstein.G_contra_ii | G_contra_ii_expr | DOM.REAL_BRANCH | 4d6efe1d6f69e3a8 |
| flrw.tf.e05.G00_to_partial_term | einstein_to_divergence_derivative | flrw.einstein.G_contra_00 | G_contra_00_expr | flrw.divergence.expanded_nu0 | partial_G00_expr |  | 3c7e8b3d9c8b2645 |
| flrw.tf.e06.gamma_trace_to_trace_term | connection_to_divergence_assembly | flrw.connection.gamma_trace_0 | gamma_trace_0_expr | flrw.divergence.expanded_nu0 | gamma_trace_term_expr |  | fa7b00f6fbd251e6 |
| flrw.tf.e07.G00_to_trace_term | einstein_to_divergence_assembly | flrw.einstein.G_contra_00 | G_contra_00_expr | flrw.divergence.expanded_nu0 | gamma_trace_term_expr |  | 49d2361546c8fd57 |
| flrw.tf.e08.gamma_0ii_to_spatial_term | connection_to_divergence_assembly | flrw.connection.gamma_0ii | gamma_0ii_expr, spatial_multiplicity | flrw.divergence.expanded_nu0 | spatial_connection_term_expr | DOM.REAL_BRANCH | b847e61cf497a59c |
| flrw.tf.e09.Gii_to_spatial_term | einstein_to_divergence_assembly | flrw.einstein.G_contra_ii | G_contra_ii_expr, spatial_multiplicity | flrw.divergence.expanded_nu0 | spatial_connection_term_expr | DOM.REAL_BRANCH | 3c9d9185aca7a6b2 |
| flrw.tf.e10.term_fields_to_divergence_expr | intra_divergence_assembly | flrw.divergence.expanded_nu0 | partial_G00_expr, gamma_trace_term_expr, spatial_connection_term_expr | flrw.divergence.expanded_nu0 | divergence_expanded_expr | DOM.REAL_BRANCH | 3ddba68bf3050a33 |
