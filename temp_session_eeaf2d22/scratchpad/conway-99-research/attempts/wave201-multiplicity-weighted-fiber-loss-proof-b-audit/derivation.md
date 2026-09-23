# Compact hostile derivation

For one pair fiber with positive full multiplicities `r_z`,

```text
rho=sum_z(r_z-1).
```

For distinct selected values with multiplicities `m_y<=r_y`,

```text
rho-sum(m_y-1)
 =sum_selected(r_y-m_y)+sum_unselected(r_z-1)>=0.
```

Thus a non-baseline fiber dominates `sum(m_y-2)`. In a degree-five fiber
with `k>=1`, subtracting its one unavoidable repeat leaves the preceding
nonnegative residual plus `k-1`. The empty case uses `rho>=1`.

At `c_x=13`, the two Hilton--Milner equality templates have exactly three
degree-five fibers, so exactly three baselines are removed. At
`c_x<=12`, the nonnegative term `36-3c_x` requires no template. Hence

```text
delta_x>=sum_at_x(m_y-2),
delta>=3q-epsilon.
```

Elimination with the Wave198 `q` identity gives

```text
9SF+9g+3SH+delta+epsilon-3eta>=891.
```

The multiplied Wave198 budget minus this row is

```text
32SI+48S2+8SE2+28RA+12SL+4SF+4delta+8eta
+4a1+24b3+8c2+16W>=0.
```

Therefore `B>=891`, `Q0>=7058.7`, and conditionally `Q>=7059`.
