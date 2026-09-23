# Compact derivation

At center `x`, for each pair fiber put

```text
rho_P=d_P-u_P.
```

Full leaf multiplicities give

```text
rho_P>=sum_selected_nonprivate(m_y-1).
```

If `c_x<=12`, the spare term `36-3c_x` immediately yields
`delta_x>=sum(m_y-2)`.

If `c_x=13`, Hilton--Milner equality has exactly three degree-five pair
types. Subtract one baseline loss from each. In a degree-five fiber with
`k>=1` selected nonprivate leaf values,

```text
rho_P-1
 >=sum(m_y-1)-1
 =sum(m_y-2)+(k-1).
```

The empty case is covered by `rho_P>=1`; other fibers need no baseline
subtraction. Therefore globally

```text
delta>=3q-epsilon.
```

Combining this with

```text
4q=297-3SF-3g-SH+epsilon+delta+eta
```

gives

```text
9SF+9g+3SH+delta+epsilon-3eta>=891.
```

The Wave198 budget exceeds this left side by

```text
32SI+48S2+8SE2+28RA+12SL
+4SF+4delta+8eta+4a1+24b3+8c2+16W,
```

so `B>=891`, `Q0>=7058.7`, and `Q>=7059`.
