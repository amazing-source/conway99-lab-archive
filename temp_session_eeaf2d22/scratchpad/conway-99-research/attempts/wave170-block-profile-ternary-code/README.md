# Wave 170: block profiles, clique geometry, and ternary rank

Status: `DERIVED_STRATEGY`; independent verification is required before
promotion.

Continue in the Wave 168 block-intersection graph `K`. For a triangle block
`L`, let `n_j(L)` count disjoint triangle blocks joined to `L` by exactly
`j` cross edges, and put `p_L=n_3(L)`.

Exact pointwise counting gives

```text
(n0,n1,n2,n3)
 = (32-p_L, 144+3*p_L, 36-3*p_L, p_L).
```

Thus `0<=p_L<=12`, and at the prism-free endpoint every block has the
uniform profile

```text
(32,144,36,0).
```

Globally, for unordered disjoint block pairs,

```text
N3=P,
N2=4158-3*P,
N1=16632+3*P,
N0=3696-P.
```

The `N2` pairs are exactly the six-vertex `N3` motif, recovering

```text
n3+3*P=4158
```

inside the triangle-incidence space.

The 99 original points give 99 maximum `K7` point-star cliques in `K`;
each edge of `K` belongs to exactly one such star and every block vertex
belongs to three. Over `F_3`, the point-block Gram has exact rank 55:

```text
rank_F3(B*B^T)=55,
55<=rank_F3(B)<=98.
```

These facts suggest a star-complement or ternary-code classification of the
132-dimensional `-3` eigenspace coupled to the 99 clique rows. They add exact
higher-order structure but no new numerical `P` or `n3` bound yet.

No endpoint exclusion, graph, novelty, or Conway-99 resolution is claimed.
