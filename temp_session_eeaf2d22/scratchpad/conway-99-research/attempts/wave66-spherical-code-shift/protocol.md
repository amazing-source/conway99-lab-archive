# Wave 66 protocol: spherical/equiangular lattice shift

Date frozen: 2026-07-27

Role: discovery

Claim label: `CANDIDATE`

## Frozen hypothesis

Assume that an adjacency matrix \(A\) of an
\(\operatorname{srg}(99,14,1,2)\) exists.  Thus

\[
A^2=12I-A+2J,\qquad AJ=JA=14J.
\]

No automorphism, vertex-transitivity, or restricted search is assumed.

Put

\[
S=2A-J+I,\qquad r=\operatorname{rank}_{\mathbf F_7}(S).
\]

This sign convention is fixed throughout: adjacent off-diagonal entries of
\(S\) are \(+1\), nonadjacent off-diagonal entries are \(-1\), and
\(S\mathbf1=-70\mathbf1\).

The imported, independently verified facts used in the low-norm argument are:

1. \(\operatorname{rank}_{\mathbf F_2}(A)=54\) and
   \(\operatorname{rank}_{\mathbf F_3}(A)=45\);
2. the binary code \(\ker_{\mathbf F_2}(A)\) has minimum weight at least
   eight;
3. a weight-eight word in that kernel has independent support, and every
   graph vertex meets that support in zero or two vertices.

## Question

Translate the graph into its primitive-idempotent spherical embedding, then
into an exact integral lattice.  Determine:

- the lattice rank, parity, determinant, and discriminant group;
- the signature/Milgram congruence forced on \(r\);
- a rigorous lower bound on the dual minimum;
- whether these consequences contradict the currently verified interval
  \(28\le r\le44\).

## Separation and status rules

- This package is discovery work and cannot verify itself.
- `CANDIDATE` means an exact derivation awaiting an independent verifier.
- A surviving determinant row is not a lattice construction and not a graph.
- No literature-priority or novelty claim is made; novelty is `UNKNOWN`.
- All computations are parameter-level exact arithmetic, not a graph search.
