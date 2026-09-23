# Boundary and failed continuations

## Subtracting the baseline edge is invalid

When `x~t` in the shared-center case, every outer `x`-star block is disjoint
from `T` but still has the cross edge `xt`.  The verified centered table is

```text
D(T,S)=j(T,S) mod 3
```

for disjoint blocks, not `j-1`.  Omitting the baseline would create the
incorrect pairing profiles `1,2,0^5` or `1^3,0^4`.  The correct
prism-free profile is five ones and two twos, which projector singularity
rejects immediately.

## A Gram-kernel vector is not automatically a circuit

The checkerboard vector in (5) is orthogonal to the four displayed columns.
If their span were degenerate, that fact alone would not make it a true
column relation.  Wave 181 uses it only after starting from an existing
multiplicity-two circuit.  To prove that every canonical square is a conic,
one must establish all 2,079 true relations, equivalently the equality face
in Section 5.

## The first conic-projector sum vanishes

Every triangle block occurs in 36 canonical squares.  Characteristic three
therefore kills the total of all 2,079 conic-plane projectors.  A first
moment in `Sym^2(V)` cannot exclude the equality face.

## A rank-221 theorem is still missing

The exact target is the signed matrix

```text
R_square^T R_square=2K+L mod 3.
```

The known rank cap `rank(R_square)<=220` is conditional on equality.  No
parameter-only lower bound above 220 has been proved.  Numerical rank on a
constructed graph is unavailable because no target graph is known, and a
search for one would violate the analytic scope of this wave.

## Even a one-unit improvement is not Conway-99

Proving `rank(R_square)>=221` would imply at least 2,080
nonedge-realizing circuits and raise the dual short-word bound by two.  It
would sharpen the conditional rank-11 enumerator boundary, not exclude the
endpoint by itself.
