# Wave 150 protocol

## Frozen statement

Assume only a hypothetical finite simple graph with parameters
`srg(99,14,1,2)` and test the conditional endpoint `n3=4158`.  Do not assume
an automorphism, vertex transitivity, or that an aggregate count vector is a
graph.

## Required rows

Use exactly:

- the frozen 170 Wave 44 equations;
- all 208 Wave 147 ordinary deletion rows;
- all 944 Wave 148 marked-vertex rows;
- all 4,440 Wave 148 pointwise ordered-pair rows;
- nonnegative order-seven and order-eight counts;
- total subset counts; and
- both Wave 147 ordered-pair centered covariance matrices.

## Exact witness rule

A promoted null witness must:

1. specify every positive order-seven and order-eight count;
2. use exact integers or rational strings;
3. replay every linear row exactly;
4. replay every centered matrix entry exactly;
5. remain nonnegative;
6. record the finite-field rank used to select the rational subsystem; and
7. be checked independently without importing discovery code.

Floating solver status is never a certificate.  A solver-infeasible result
that changes under an equivalent nonnegativity encoding is a failed route.

## Scope

An exact feasible vector proves only that this relaxation cannot exclude the
endpoint.  It neither constructs a graph nor establishes novelty.
