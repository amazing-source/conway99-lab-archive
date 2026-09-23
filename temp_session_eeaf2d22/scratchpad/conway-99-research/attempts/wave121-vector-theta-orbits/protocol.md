# Wave 121 discovery protocol

## Frozen scope

- Conditional row: `q=14`, `rank_F7(S)=30`.
- Scalar theta range: `x7,...,x14`.
- Extended dual range: `y1,...,y77`.
- Target shells: `K` norms 20 and 22.
- Inputs: sealed verified Wave 66/80/86/97/101 packages.
- Secondary C4 lane: rank-28 scalar Jacobi marking through `q^10`, frozen
  against verified Waves 71/112/116.

## Separation and status

1. This directory is discovery work and cannot mark itself `VERIFIED`.
2. Full orthogonal exact-value aggregates are allowed; component equality
   and lifted automorphisms are forbidden.
3. Projective orbit collapse is forbidden.
4. Norm-20 and norm-22 coordinate compositions stay unknown unless proved
   independently.
5. Rational feasibility, integral coefficient feasibility, lattice
   realization, and graph realization are separate statuses.
6. A finite formal theta prefix is not a lattice.
7. No absence conclusion follows from an incomplete coefficient range.
8. A truncated Jacobi coefficient table is not a Jacobi form.
9. The `q^10` scalar Jacobi coefficient has no short-pattern interpretation
   unless the coordinate alphabet is independently extended.

## Reproducibility

The script checks all frozen manifest hashes before calculation, regenerates
the exact modular basis through degree 77, and refuses to start below 15%
free physical memory.
