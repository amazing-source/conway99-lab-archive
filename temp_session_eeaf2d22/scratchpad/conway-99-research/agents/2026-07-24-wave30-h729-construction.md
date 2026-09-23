# Wave 30 construction: a rootless rank-20 `h=729` block and rank-44 control

```yaml
role: construction
date_utc: 2026-07-24T04:14:28Z
git_commit: ff6902812c46d33bd081e7580d09baa1d60a5494
claim_label: CANDIDATE
scope: >-
  Exact construction of a rootless even positive-definite rank-20
  determinant-729 lattice T20 with 3*T20^-1 and 21*T20^-1 even integral,
  and the bare rank-44 S/G candidate T20 orthogonal_sum LAMBDA24. No Q,
  B, projector frame, Schur-square realization, graph, endpoint exclusion,
  or Conway-99 resolution is claimed.
inputs:
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  verification/wave28-simultaneous-neighbor/independent_check.py: 2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db
  verification/wave28-theta-modular/independent_check.py: 513efd1a915bc14adc3003c41e6758839375d9a36a0055f08faa56417c942b18
method: >-
  Five explicitly frozen exact two-neighbors from K12 orthogonal_sum E8;
  checked rational neighbor bases; contragredient scaled-dual transport;
  deterministic unimodular exact LLL after each step; complete reverse-LDL
  integer-ellipsoid enumeration through norm two after every neighbor and
  through norm four at the endpoint; then an exact direct sum with an
  attributed embedded Leech Gram matrix independently checked through norm
  two.
command: |-
  cd attempts/wave30-h729-construction
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave30-h729-construction/exact_check.py: 6415f40948f5033fff47c1f090776f417ac0a8cd0adf589cb5d4aa66cbb7d852
  attempts/wave30-h729-construction/test_exact_check.py: 0bd86cadac900ddcfb34d6c76bfa827fe94cc001ef75d1c9c9e6b008d7373cd5
  attempts/wave30-h729-construction/exact-results.json: 0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11
  attempts/wave30-h729-construction/input-freeze.sha256: 895ce37d214acf92aa5c4f2bd1eaaadaa8ef625045e31479b25eb4f42caf17fe
  attempts/wave30-h729-construction/failed-routes.md: 51d6a9681b5fdddc6dffe70baf1f80f03a2b652440ebd5506cfce0dced440115
limitations:
  - The five-neighbor route is a construction, not a complete neighbor-graph or isometry classification.
  - The rank-44 object uses the explicit orthogonal T20 plus LAMBDA24 ansatz.
  - Shell size does not construct either required tight frame.
  - No even determinant-five Q or compatible B is supplied.
  - No X, M, W, Schur identity, graph, n3=708 realization, or target resolution is supplied.
  - Discovery output is FINITE_COMPUTATIONAL_EVIDENCE and requires a fresh independent verifier.
```

## Result and status wall

There is an exact rootless rank-20 lattice `T20` with

```text
rank(T20)=20,
det(T20)=729,
min(T20)=4,
# {x : x^T T20 x=4}=5076,
3 T20^(-1) even integral,
21 T20^(-1) even integral.
```

Its canonical Gram-matrix hash is

```text
1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6.
```

Taking the direct sum with the displayed Leech Gram matrix gives

```text
S44 = T20 orthogonal_sum LAMBDA24,
G44 = 21 S44^(-1),
rank(S44)=44,
det(S44)=729,
min(S44)=4,
S44 G44=21 I44,
S44 and G44 even integral positive definite.
```

The complete `44 x 44` matrices are in `exact-results.json`, with hashes

```text
S44: 3fbeb977e268913f8eb2f2b9b27897eb954ad73ccd66cdb8e124b13b6527303b
G44: c3402926e02395a3e932e0ca2d7f2f0aa3550e7cbd856c0ac76441b4921e211e.
```

This gives a new exact construction route at the bare lattice layer and
instantiates the rank split independently identified as the surviving
decomposable rootless boundary by the separate Wave 30 structural lane.  It
does not prove that the structural lane is correct, and neither lane verifies
the other.

The publication-safe status is:

```text
rootless rank-20 determinant-729 T20:              CANDIDATE
rootless rank-44 bare S/G package:                  CANDIDATE
evidence label:                                     FINITE_COMPUTATIONAL_EVIDENCE
determinant-five Q and endpoint B:                  NOT CONSTRUCTED
231-row projector/Schur package:                    NOT CONSTRUCTED
n3=708:                                             UNKNOWN
Conway-99 and novelty:                              UNKNOWN
```

## 1. Frozen starting lattice

The construction starts from

```text
L0=K12 orthogonal_sum E8.
```

The `K12` Gram matrix is the attributed matrix already independently checked
in Wave 28.  The `E8` matrix is regenerated from its Cartan diagram.  Exact
elimination and enumeration give

```text
rank(L0)=20,
det(L0)=729,
min(K12)=4,
roots(K12)=0,
roots(E8)=240,
roots(L0)=240.
```

Both `L0` and `21 L0^(-1)` are even integral and positive definite.  No
automorphism of a target, of `L0`, or of a later neighbor is assumed.

## 2. Exact two-neighbor operation

At one step let `A` be the current integral Gram matrix and let
`v in Z^20` be the frozen binary vector indicated by its support.  Put

```text
H={x in Z^20 : x^T A v=0 mod 2},
L' = H + Z(v/2).
```

Every accepted vector has

```text
v^T A v=0 mod 8,
```

and a nonzero parity functional.  The checker constructs a basis `P` for
`L'` directly: first an index-two basis of `H`, then one primitive column is
replaced by `v/2`.  It checks

```text
det(P)=+/-1
```

over the rationals and forms

```text
A'=P^T A P.
```

The determinant is therefore preserved.  The scaled dual is transported
contragrediently:

```text
21(A')^(-1)=P^(-1)(21A^(-1))P^(-T).
```

At every step the checker verifies all entries, even diagonals, exact
positive-definite LDL pivots, determinant `729`, and the displayed identity.
Not every two-neighbor would preserve the even scaled-dual condition; it is
checked rather than inferred for the five selected neighbors.

## 3. The five-neighbor certificate

Coordinates in each row below refer to the exact reduced basis produced by
the preceding row.

| step | support of `v` | `v^T A v` | exact roots after step | reduced Gram hash |
|---:|---|---:|---:|---|
| 0 | start `K12+E8` | - | 240 | - |
| 1 | `0,1,2,5,11,13,14,17,18` | 24 | 112 | `9374ae66ba0bdede1cbd0649eb3957981784d09c60b60831733ea8e445f2045d` |
| 2 | `5,7,8,9,10,11,12,13,14,19` | 72 | 48 | `1433fc399784634e5e3101581182a5cbc2a9d12d811798bef8d37f4d59d7a674` |
| 3 | `1,4,6,10,11,14,16,17,19` | 56 | 20 | `1c0589783b5cf6652a902f8eb0ac706dd54d8243c72395d974f515bea1748a3f` |
| 4 | `3,4,5,6,7,8,10,12,14,15,17,19` | 64 | 6 | `242c3380102a5a1e69e8d51dbe3771936e4b08d4104234cd7dd5e4c58332774a` |
| 5 | `0,5,6,8,9,10,13,14,15,16,17,18,19` | 88 | 0 | `1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6` |

After each neighbor, an exact LLL routine returns an integer unimodular row
matrix `U` and replaces `A'` by

```text
U A' U^T.
```

This changes only the basis, not the lattice or its roots.  Every rational
neighbor basis `P`, its inverse, every integral `U`, intermediate hash, and
enumeration telemetry is included in the JSON certificate.

## 4. Complete root and norm-four enumeration

For a positive-definite exact LDL decomposition

```text
A=L D L^T,
```

the checker enumerates integer coordinates in reverse order.  At each node it
uses an integer square-root bound on the remaining exact rational ellipsoid.
Floating point is not used to accept, reject, or bound a coordinate.

The final norm-two search visits `3094` accepted partial nodes and only the
zero leaf.  The norm-four search visits `128154` partial nodes and gives

```text
norm 0:    1 vector,
norm 2:    0 vectors,
norm 4: 5076 vectors.
```

The complete sorted norm-four shell has canonical hash

```text
7b83bccafcd31ee04e0c028f10f51363d3c3b0a22f5f87dc9bbbd14875ca6010.
```

This is a finite complete enumeration for this exact Gram matrix, not a
classification of rank-20 lattices.

## 5. Exact level and scaled dual

Direct inversion gives the complete integer matrix

```text
G20=21 T20^(-1),
```

whose hash is

```text
006011e5ea2fa29cc942bcaa3e72e6d300a549fbad6b6991f3edffb20371a024.
```

The checker also verifies `3 T20^(-1)` is even integral.  Since
`det(T20)=3^6>1`, the exact level is three.  The weaker frozen endpoint
requirement with scale 21 follows immediately and is also checked entry by
entry.

## 6. Rank-44 assembly

The embedded `LAMBDA24` matrix comes from the Nebe--Sloane lattice catalogue:

```text
https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/Leech.html
```

The source response hash observed on `2026-07-24` is retained, but the HTML
body is not.  Independently of the catalogue metadata, the checker proves for
the embedded matrix:

```text
rank=24,
determinant=1,
even integral and positive definite,
inverse even integral,
no vector of norm two.
```

The exact norm-two ellipsoid enumeration visits `40672` partial nodes and
only the zero leaf.  Thus both direct summands have minimum four.  Any norm-two
vector in their orthogonal sum would have to be a root in one summand, so the
rank-44 candidate is rootless without a restricted 44-dimensional search.

The block determinants and ranks are

```text
(20,729) + (24,1) = (44,729).
```

The full direct sum also has `3S44^(-1)` and `21S44^(-1)` even integral, so
it has exact level three and passes every bare `S/G` condition frozen for the
`h=729` row.

## 7. What the shell says—and does not say—about a frame

If this particular orthogonal decomposition carried the full frame, minimum
four would force every norm-four row into one block.  The trace of the
second-moment identity would require

```text
T20 rows:       21*20/4 = 105,
LAMBDA24 rows:  21*24/4 = 126.
```

The `5076` signed norm-four vectors of `T20` give `2538` antipodal lines, so
the rank-20 shell is not eliminated by the elementary availability count.
That is the strongest justified frame statement.

A restricted Boolean scout imposed all `210` upper-triangular equations of

```text
X_A^T X_A=21T20^(-1)
```

on the `2538` lines.  Z3 returned `unknown` at a 30-second timeout.  The
nonhit is retained in `failed-routes.md` and is not evidence.  Even a
second-moment witness would still need orientations and pairwise products in
`{0,1,-1,-2}`, the exact row data, cubic constraints, the complement frame,
and Schur origin.

## 8. Strongest objection and next boundary

The decisive missing object is not another bare lattice.  It is an exact
rank-20 coupled certificate:

```text
Q_A even integral positive definite,
det(Q_A)=5,
B_A=T20 Q_A=I mod 2,
tr(B_A)=36,
```

together with `105` actual shell rows whose second and third moments produce
that `Q_A`.  None is supplied here.  The formal scalar spectrum

```text
spec(B_A)=5^1,3^6,1^13
```

matches determinant and trace but is not a lattice endomorphism certificate.

Accordingly, the new construction strengthens the hostile-control side of the
research: the last decomposable rootless *bare lattice shape* is nonempty.
It does not show the full endpoint shape is nonempty and does not weaken any
verification gate.
