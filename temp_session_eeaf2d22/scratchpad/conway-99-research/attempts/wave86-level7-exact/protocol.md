# Wave 86 protocol: exact level-7 theta pair

Date frozen: 2026-07-28 UTC.

Role: discovery.

Claim label: `DERIVED`.

## Imported hypotheses

This package inspects only the independently verified Wave 66 and Wave 71
consequences.  It is conditional on a hypothetical
`srg(99,14,1,2)` and on the Wave 71 row `q=16`:

- `L` and `K=sqrt(7)L*` are even positive-definite rank-44 lattices of
  exact level seven;
- `det(L)=7^16`, `det(K)=7^28`, and both scalar theta series have trivial
  character in weight 22;
- `min(K)>=14`;
- with `x_n=[q^n]Theta_K`,
  `x_1=...=x_6=0` and
  `x_7+x_8+x_9=2 (mod 14)`.

No automorphism, endpoint, or transitivity hypothesis is imported.

## Question

Does the exact level-7 modularity and Fricke exchange of the two theta
series strengthen the Wave 71 mod-7 shadow?

## Separation rules

- Discovery does not verify itself.
- Scalar theta feasibility is not lattice-genus feasibility.
- Lattice-genus feasibility is not existence of the marked 99-frame.
- Solver exit codes and numerical optimization are not certificates.
- Conway-99 and novelty remain `UNKNOWN`.
