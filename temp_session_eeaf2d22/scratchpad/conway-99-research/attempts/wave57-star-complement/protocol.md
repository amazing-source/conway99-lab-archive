# Wave57 star-complement and spectral-compression protocol

## Frozen conditional statement

Assume that a Conway-99 graph exists and attains the Wave35 endpoint
`n3 = 4158`.  Thus the graph is a strongly regular graph with parameters
`srg(99,14,1,2)`, spectrum `14^1, 3^54, (-4)^44`, no triangular prism,
and disjoint-triangle profile `(32,144,36,0)`.

Fix one triangle `T = {t0,t1,t2}`.  Let `Xi` be the 12 neighbours of `ti`
outside `T`, put `X = X0 union X1 union X2`, and let `Y` be the remaining
60 vertices.  The frozen cell sizes and equitable neighbour counts are

```
       T   X   Y
T      2  12   0
X      1   3  10
Y      0   6   8
```

Every vertex of `Y` has exactly two neighbours in each `Xi`.  The graph
induced by `X` is cubic and triangle-free, and the graph induced by `Y`
is 8-regular.

This run assumes no automorphism, transitivity, canonical labelling, or
normal form.  All reductions apply to an arbitrary fixed triangle.

## Frozen questions

1. Derive the quotient spectrum and all eigenvectors forced to be supported
   on `U = T union X`.
2. Convert those supported eigenvectors into exact restrictions on the
   multiplicities of eigenvalues `3` and `-4` in `G[Y]`.
3. Quantify how many vertices of `U` every corresponding star set must hit.
4. Combine trace, triangle, four-cycle, and compact-interval moment
   constraints into an exact finite feasibility ledger.
5. State a smaller exact star-complement compatibility problem and test
   whether these consequences alone contradict the endpoint.

## Status discipline

The target graph and endpoint begin and end as `UNKNOWN` unless an independently
checkable contradiction or complete construction is produced.  A scalar
spectral control is not a graph spectrum.  A star-complement reconstruction
identity is not an existence certificate until its binary incidence data and
induced graph are supplied and checked.

## Frozen inputs

The input hashes are recorded in `input-freeze.sha256`.  The principal
mathematical inputs are:

- `attempts/wave35-n3-4158-combinatorial/exact-results.json`;
- `attempts/wave35-n3-upper-spectral/exact-results.json`;
- `verification/wave35-n3-upper-spectral/independent-results.json`;
- `verification/wave35-n3-upper-spectral/audit.md`.

## Star-complement references

- D. Cvetkovic, P. Rowlinson, and S. Simic, "A study of eigenspaces of
  graphs," *Linear Algebra and its Applications* 182 (1993), 45-66,
  DOI `10.1016/0024-3795(93)90491-6`.  This is the primary source used
  for star bases.
- D. Cvetkovic, P. Rowlinson, and S. Simic, "Some characterizations of
  graphs by star complements," *Linear Algebra and its Applications*
  301 (1999), 81-97, DOI `10.1016/S0024-3795(99)00179-2`.
- D. Cvetkovic, P. Rowlinson, and S. Simic, *An Introduction to the Theory
  of Graph Spectra*, chapter "Structure and one eigenvalue," Cambridge
  University Press, DOI `10.1017/CBO9780511801518.006`.

The 1993 and 1999 articles are the primary literature used here.  The book
chapter is an authoritative modern statement of the star-set/projector and
Reconstruction Theorem facts.  Every graph-specific calculation in this run is
reproduced by the local standard-library checker.
