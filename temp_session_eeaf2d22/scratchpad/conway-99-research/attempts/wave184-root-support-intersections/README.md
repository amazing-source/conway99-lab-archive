# Wave 184: sparse root-support intersections

Status: `DERIVED_PENDING_VERIFICATION`.

Under the verified Wave 183 setting, distinct global-root supports intersect
in at most two vertices; an intersection of size two is a graph edge.

Every internal graph edge of a root support yields a distinct projective
weight-four outer-star circuit.  If `n_i` counts roots of multiplicity
`i=5,6,7`, the number of these circuits is exactly

```text
E=3*n_6+7*n_7.
```

The incidence equation `5*n_5+6*n_6+7*n_7=2079` forces `E>=12`.
Together with the 2,079 canonical quadrilateral conics, Wave 181 equality
therefore implies

```text
at least 2,091 projective weight-four circuits,
B_4>=4,182.
```

This is an exact conditional short-word refinement, not an exclusion of
Wave 181 equality, rank 11, the endpoint, or Conway-99.

