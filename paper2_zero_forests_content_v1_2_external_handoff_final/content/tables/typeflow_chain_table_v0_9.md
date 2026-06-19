| role | subleaf_id | type | purpose |
| --- | --- | --- | --- |
| root | flrw.metric.scale_factor | metric definition | source of selected connection and Einstein tensor exports |
| intermediate | flrw.connection.gamma_trace_0 | connection scalar export | feeds gamma-trace divergence term |
| intermediate | flrw.connection.gamma_0ii | connection scalar export | feeds spatial connection divergence term |
| intermediate | flrw.einstein.G_contra_00 | Einstein tensor scalar export | feeds partial derivative and trace product terms |
| intermediate | flrw.einstein.G_contra_ii | Einstein tensor scalar export | feeds spatial product term |
| sink | flrw.divergence.expanded_nu0 | assembled tensor scalar expression | selected contracted Bianchi zero obligation |
