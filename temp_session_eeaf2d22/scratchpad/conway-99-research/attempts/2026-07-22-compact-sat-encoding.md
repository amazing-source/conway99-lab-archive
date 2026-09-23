# Compact exact SAT encoding

- Status: `VERIFIED` for encoding exactness and small-instance semantics;
  target satisfiability remains `UNKNOWN`
- Scope: unrestricted rooted residual problem; no completed-graph automorphism
  assumption

Let `x[p,q]` encode residual adjacency. The 1,176 endpoint-profile equalities
from the rooted block equation are

```text
sum_{q != p, u in label(q)} x[p,q]
  = 2 - 1[u in label(p)] - 1[mate(u) in label(p)].
```

They force degree 12 at every residual vertex and therefore 504 residual edges.

For each unordered pair `p,q` and third vertex `r`, introduce `y[p,q;r]` but
only add the one-way implication

```text
x[p,r] and x[q,r]  ->  y[p,q;r].
```

Then impose the upper bound

```text
sum_r y[p,q;r] + x[p,q] <= 2 - |label(p) intersection label(q)|.
```

This apparently one-sided encoding is exact. There are 924 intersecting label
pairs. The degree constraints force exactly

```text
84 * binom(12,2) = 5,544
```

actual residual wedges, while the sum of all common-neighbor upper bounds after
moving the 504 edge variables to the right is

```text
2 * binom(84,2) - 924 - 504 = 5,544.
```

Every actual wedge forces its corresponding `y` true. Since every pairwise
quantity is bounded above and the sums of the actual quantities and bounds are
equal, every bound is attained individually. Spurious `y` values and deficient
common-neighbor counts are therefore impossible.

The implemented compact form has:

- 3,486 primary residual-edge variables;
- 285,852 one-way wedge variables and link clauses;
- 1,176 exact endpoint-profile cardinalities;
- 924 at-most-one common-neighbor cardinalities; and
- 2,562 at-most-two common-neighbor cardinalities.

`code/sat_model.py` retains a larger `direct` variant with full conjunction
equivalences and exact common-neighbor cardinalities. Positive and negative
small cases must agree across both variants before target runs.
