# Wave 176: star projectors and forced cross-star circuits

Status: `DERIVED_PENDING_VERIFICATION`.

At the conditional endpoint rank `k=11`, each of the 99 labelled
seven-triangle stars spans a nondegenerate six-space.  Its seven centered
columns form the Gram simplex `J_7-I_7`, so they define a canonical
orthogonal projector

```text
P_x=-sum_(T contains x) z_T tensor z_T.
```

This produces two analytic constraints without searching for a graph:

```text
rank_F3((tr(P_x P_y))_(x,y))<=65,
every pair of distinct vertex-stars has a genuinely cross-star relation.
```

For adjacent vertices, the outer cross-incidences form a 2-regular
bipartite graph on `6+6` vertices.  Its four possible cycle types have
centered Gram ranks

```text
cycle type       6   4+2   3+3   2+2+2
Gram rank       10    10     8       9
```

The radical inequality in an 11-dimensional nondegenerate space then
forces at least one cross-star relation in every type.  Types `6` and
`4+2` have exact cross-coset minimum supports 8 and 4 respectively.

This is a structural ternary-matroid and finite-geometry reframing, not a
brute-force construction.  It does not eliminate the endpoint: residues
of the nonedge projector traces and the global compatibility of the
cross-star circuits remain uncontrolled.
