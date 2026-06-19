# FLRW AST-path inventory v0.7

The selected FLRW contracted-Bianchi expression is mapped from named tensor subleaves into route expressions using AST paths rather than literal spans.

```text
diff(3*H**2, t) + 3*H*3*H**2 + 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
```

The n-ary AST view is:

```text
$.terms[0] = diff(3*H**2, t)
$.terms[1] = 3*H*3*H**2
  $.terms[1].factors[0:2] = 3*H
  $.terms[1].factors[2:4] = 3*H**2
$.terms[2] = 3*(H*exp(2*H*t))*(-3*H**2*exp(-2*H*t))
  $.terms[2].factors[1:3] = H*exp(2*H*t)
  $.terms[2].factors[3:6] = -3*H**2*exp(-2*H*t)
```

The full divergence scalar export uses `$` as the path.

