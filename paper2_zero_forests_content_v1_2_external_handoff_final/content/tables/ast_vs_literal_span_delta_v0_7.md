| property | v0.6 literal span | v0.7 AST path |
| --- | --- | --- |
| authority | character offsets | structural path |
| formatting robustness | fragile | whitespace/redundant parentheses tolerated |
| audit readability | very concrete | concrete plus structural |
| commutative reordering | not supported | not silently supported; future v0.8 target |
| tamper target | span/hash drift | path/hash/payload drift |
