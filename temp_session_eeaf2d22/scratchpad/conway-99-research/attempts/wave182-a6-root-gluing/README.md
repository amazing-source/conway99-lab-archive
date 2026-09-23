# Wave 182: gluing 99 local A6 root systems

Status: `DERIVED_PENDING_VERIFICATION`.

Assume equality in the verified Wave 181 nonedge circuit bound:

```text
Q=2079.
```

Then every canonical induced quadrilateral is a checkerboard conic.  Its
relation assigns to each nonedge `xy` a norm-one projective vector

```text
rho_xy in E_x intersect E_y.
```

For a fixed vertex `x`, these labels form the 21 projective differences of
the seven-point star simplex, a negative `A6` root system.  Each local root
labels exactly four of the 84 nonedges at `x`.

Equality makes the gluing rigid:

```text
R_x intersect R_y={rho_xy} for every nonedge xy.
```

For every global root `r`, the vertices whose local root system contains
`r` induce a 4-regular graph in the complement.  Exact SRG and edge-circuit
counts give

```text
5<=m_r<=10,
sum_r m_r=2079,
sum_r binomial(m_r,2)<=8316,
231<=number of global roots<=415.
```

If the lower extreme 231 occurs, every root lies in exactly nine stars,
every adjacent star pair shares six roots, and every edge has local cycle
type `3+3` with all six eligible weight-four relations true.

The local root frames satisfy

```text
sum_(r in R_x) r tensor r=-P_x,
sum_r m_r r tensor r=0.
```

At the 231-root extreme, `m_r=9=0 mod 3`, so the global frame identity is
coefficientwise trivial.  This is a rigid finite-root/design boundary, not
an endpoint contradiction.

No graph, code, SAT, configuration, or isomorphism search is used.  Equality
`Q=2079`, rank 11, the endpoint, and Conway-99 remain `UNKNOWN`.
