# Wave 28 candidate freeze: simultaneous two-neighbor hostile controls

Frozen by the orchestrator on 2026-07-24 from public branch head
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`.

Primary status: `CANDIDATE`

This is an orchestrator-discovered exact construction target for a fresh
independent checker.  The figures below are not accepted as `VERIFIED`.

## Frozen input

Use the exact Wave 27 arithmetic package

```text
S = E8^4 orthogonal_sum E6^2
Q = (E8^(-1))^4 orthogonal_sum Q6^2
G = 21 S^(-1)
B = S Q
```

from `attempts/wave27-a2free-construction/exact_check.py`, whose SHA-256 is

```text
1bd20f820a5d4467f29860a03a93c4ef3192bb9df4b1c87901080ffa8b793f1e
```

The Wave 28 orchestrator brief SHA-256 is

```text
6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
```

## Candidate construction

Coordinates are zero-based in the displayed Wave 27 block basis.  The
preferred control, which meets all six displayed blocks, is

```text
support(v) = {3,6,9,18,25,33,35,41}.
```

The initially found control is retained separately:

```text
support(v_initial) = {0,3,11,14,22,28,30,42}.
```

For either frozen support, put

```text
v_i = 1 on support(v), and 0 otherwise
a = S v
```

Define the index-two sublattice and its even two-neighbor

```text
H = {x in Z^44 : x^T S v = 0 (mod 2)}
L' = H + Z (v/2).
```

Let `P` be any rational basis matrix whose columns form a basis of `L'`.
The verifier must construct `P` deterministically and check
`det(P)=+-1`; it must not trust a submitted matrix inverse.  Define

```text
S' = P^T S P
Q' = P^(-1) Q P^(-T)
G' = P^(-1) G P^(-T)
B' = S' Q'.
```

The exploratory exact calculation gave

```text
v^T S v       = 16
a^T Q a       = 16
a^T G a       = 336.
```

These congruences are intended to make all three transformed forms even and
integral.  That implication and every transformed entry must be checked
independently.

## Expected exact invariants to attack

The independent checker should confirm or refute all of:

```text
S', Q', G' are symmetric, even, integral, and positive definite
S' G' = 21 I
det(S') = 9
det(Q') = 9
B' = I (mod 2)
tr(B') = 60
det(B') = 81
tr((B'-I)/2) = 8
tr(((B'-I)/2)^2) = 32
```

It should emit the complete `S',Q',G',B',C'` matrices in machine-readable
form with SHA-256 hashes.

## Expected root censuses

Enumerate every norm-two vector of `S'` exactly.  A direct 44-dimensional
reverse-LDL exploratory run exceeded 124 seconds and was stopped; that
timeout is not evidence.

For the preferred all-six-block support, a block-coset enumeration gave:

```text
new roots in (v/2)+H: 0
total roots: 568
root span rank: 43
nonorthogonality component sizes:
  2,2,2,2,30,40,112,126,126,126
component types:
  A1,A1,A1,A1,A5,D5,D8,E7,E7,E7
```

An additional exact exploratory calculation predicts the following
primitive-closure data.  These figures are also unverified targets:

```text
root lattice determinant: 12288
root-span orthogonal lattice K: <12>
divisibility of a primitive norm-12 generator in L': 3
[primitive root closure : root lattice] = 32
[L' : primitive root closure orthogonal_sum K] = 4
det(primitive root closure) = 12
[L' : root lattice orthogonal_sum K] = 128
```

In the original Wave 27 rational coordinates, the proposed generator of
`K` is zero outside the first `E6` block and is

```text
(2,1,0,-1,-2,0)
```

inside that block.  The verifier must check primitivity, membership,
orthogonality, norm, divisibility, and every determinant/index identity.
If correct, this control explicitly realizes both gluing stages `H0,H1`
from the separate Wave 28 glue/discriminant reduction.

For the retained initial support, the same method gave:

```text
new roots in (v/2)+H: 0
total roots: 568
root span rank: 44
nonorthogonality component sizes:
  2,2,30,72,112,112,112,126
component types:
  A1,A1,A5,E6,D8,D8,D8,E7
root-sublattice determinant: 9216
[L' : root_subLattice] = 32
```

The verifier should prioritize the all-six-block support and must reproduce
both root cosets completely, prove its norm bounds, and infer component types
from checked rank/Cartan data rather than root counts alone.  It should also
check the initial support as a hostile cross-control if resources permit.

If the preferred control is confirmed, `S'` is a genuine non-root lattice
rather than an orthogonal sum of irreducible ADE root lattices: its roots
span only rank 43.  The initial control instead has a full-rank root
sublattice of index 32 and exhibits the gluing phenomenon directly.  Either
would be an exact hostile control showing that the Wave 27
full-orthogonal-ADE hypothesis is active; the preferred control is
structurally stronger.

## Status wall

Even if every item above passes, this construction is only an abstract
arithmetic/lattice package.  It supplies no:

- primitive embedding in `Z^231`;
- 231-row norm-four projector frame;
- matrix `M` with the required entry alphabet and row profiles;
- identity `Q'=X^T(M o M)X`;
- graph;
- exclusion of `n3=708`; or
- Conway-99 resolution or novelty determination.

The independent verifier may promote only the scoped hostile control.  The
endpoint and target remain `UNKNOWN`.
