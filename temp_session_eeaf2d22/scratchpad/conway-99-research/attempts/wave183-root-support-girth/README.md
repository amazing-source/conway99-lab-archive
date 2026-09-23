# Wave 183: root-support girth and multiplicity collapse

Status: `DERIVED_PENDING_VERIFICATION`.

Assume the verified Wave 182 setting, hence in particular Wave 181 equality

```text
Q=2079.
```

For a global projective root `r`, let

```text
X_r={x:r in R_x},  m_r=|X_r|.
```

Wave 182 proves that the nonedges of `G[X_r]` form a 4-regular color graph
and that `5<=m_r<=10`.

The canonical quadrilateral involution now forbids any pair of vertices in
`X_r` from having two common neighbors inside `X_r`: for a graph edge this
is `lambda=1`; for a graph nonedge, two internal common neighbors would make
the opposite nonedge carry both the same norm-one root and an orthogonal
root.

Since `G[X_r]` is `(m_r-5)`-regular, counting internal two-paths first rules
out `m_r=9,10`.  The remaining cubic case `m_r=8` would require at least
three vertex-disjoint triangles on eight vertices, which is impossible.
Consequently

```text
m_r in {5,6,7},
297<=number of global roots<=415.
```

The induced support graphs are forced:

```text
m_r=5: 5 isolated vertices,
m_r=6: 3 disjoint edges,
m_r=7: one 7-cycle.
```

The global frame identity sharpens to

```text
sum_(m_r=7) r tensor r = sum_(m_r=5) r tensor r
```

over `F_3`; roots of multiplicity six vanish from this first tensor moment.

This is a proof-theoretic graph-girth/counting argument.  It performs no
graph, code, SAT, configuration, or isomorphism search.  Wave 181 equality,
rank 11, the prism-free endpoint, and Conway-99 remain `UNKNOWN`.

