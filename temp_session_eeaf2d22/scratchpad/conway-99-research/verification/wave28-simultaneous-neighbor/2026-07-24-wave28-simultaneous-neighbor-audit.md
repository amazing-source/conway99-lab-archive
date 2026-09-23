# Wave 28 simultaneous-neighbor adversarial audit

Verdict: **PASS for two scoped abstract arithmetic/lattice hostile controls.**

The preferred all-six-block control passes independently. The retained
initial support also passes as a chronological cross-control. No endpoint,
projector-frame, Schur-square, graph, or novelty claim is promoted.

```yaml
role: verifier
date_utc: 2026-07-24T02:37:39Z
git_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
claim_label: VERIFIED
scope: >-
  Independent exact verification of two simultaneous even two-neighbors of
  the Wave 27 E8^4 orthogonal_sum E6^2 arithmetic package. This verifies
  transformed matrices, complete root censuses, ADE component data, the
  preferred rank-43 root closure and H0/H1 indices, and the initial full-rank
  index-32 root lattice. No omitted endpoint-origin condition is verified.
inputs:
  agents/2026-07-24-wave28-simultaneous-neighbor-freeze.md: 7b8fce3763e2f6d4db2e0f7841e680d01486195d3ea4b6b04c5f59ace768d90a
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  attempts/wave27-a2free-construction/exact_check.py: 1bd20f820a5d4467f29860a03a93c4ef3192bb9df4b1c87901080ffa8b793f1e
method: >-
  Reconstruct the Wave 27 Cartan blocks and E6 extension with Fraction
  arithmetic; construct each parity-kernel/two-neighbor basis
  deterministically; compute every transformed entry; enumerate the two root
  cosets with exact reverse-LDL block bounds; reconstruct simple roots and
  Cartan diagrams; and calculate primitive closures and indices from explicit
  integer bases.
command: |-
  cd verification/wave28-simultaneous-neighbor
  python -B independent_check.py --output independent-results.json
  python -B -m unittest -v test_independent_check.py
outputs:
  verification/wave28-simultaneous-neighbor/independent_check.py: 2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db
  verification/wave28-simultaneous-neighbor/test_independent_check.py: 191206c2eb57e6a7f8fdad83115304604fe597cff42299395cf38cf9ea639e2b
  verification/wave28-simultaneous-neighbor/independent-results.json: d9f6829dc967fb3777f541b4fd16cd27acb3478d96479b8ad9c3e9fbad2afedd
limitations:
  - Both verified objects are abstract arithmetic/lattice packages only.
  - No primitive Z^231 embedding or 231-row norm-four frame is constructed.
  - No required M alphabet/profile or Q=X^T(M o M)X identity is checked.
  - The complete root systems do not certify projector or Schur compatibility.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## 1. Intake and independence

The final intake is frozen in `intake-freeze.json`. The verifier reconstructs
the `E8` and `E6` Cartan matrices from their edge sets, derives `Q6` from the
rank-one `E6`-dual projector, and forms the complete rank-44 `S,Q,G,B`
matrices. It imports no submitted Wave 27 or Wave 28 Python module and trusts
no submitted inverse or transformed entry.

The candidate freeze changed twice during verification. The checker failed
closed on the second drift. Only the final 5,150-byte freeze at
`7b8fce37...768d90a` is accepted. The superseded hashes are retained in
`failed-runs.md`.

For either support, put `a=Sv`. The independently obtained scalars are

```text
v^T S v = 16,
a^T Q a = 16,
a^T G a = 336.
```

To construct `P`, the checker chooses the first odd coordinate of `a` and
builds an explicit determinant-two basis of

```text
H={x in Z^44 : a^T x=0 (mod 2)}.
```

It expresses `v` in that basis, deterministically replaces the first
coefficient-`+-1` column by `v/2`, verifies `det(P)=1`, and computes
`P^(-1)` by fresh rational Gauss--Jordan elimination. Thus the columns of
`P` generate `H + Z(v/2)` and no submitted inverse is involved.

## 2. Complete transformed packages

For both supports, direct entrywise calculation verifies

```text
S'=P^T S P,
Q'=P^(-1) Q P^(-T),
G'=P^(-1) G P^(-T),
B'=S'Q',
C'=(B'-I)/2.
```

The three Gram forms are symmetric, even, integral, and positive definite.
Exact determinants, products, parity, and traces are

```text
S'G'=21I,
det(S')=9,
det(Q')=9,
det(B')=81,
B'=I (mod 2),
tr(B')=60,
tr(C')=8,
tr((C')^2)=32,
(C')^2=4C'.
```

In particular, `B'=I (mod 2)` and `tr((C')^2)=32` are checked directly on
the emitted matrices, not inferred from the unchanged similarity
invariants. The complete 44-by-44 matrices occur in
`independent-results.json`. Canonical JSON matrix hashes are:

| support | matrix | SHA-256 |
|---|---|---|
| preferred | `S'` | `93f25e861ba60fc2643773a814ed8bb787c757f7f367e901d528e68f93a865c6` |
| preferred | `Q'` | `c1994a92365c018e15b64228b06d2a5ab9840dc89955e3224bfa58fc5aa19ca5` |
| preferred | `G'` | `83ecb7aa586b0c4503dba58da6fcd998ca7ab740749934726acc5c9b8cfb9477` |
| preferred | `B'` | `ed80abbde30446755c0bbd9e845fd65494e9458e64aa4702ce6861527837f4a3` |
| preferred | `C'` | `3dbaab9f758745b24aab945bf51064022d42c20e367dd4f3e386218731d212b7` |
| initial | `S'` | `a80926c91a2cda135b5d7dd60a67421458358e7f8ad3e6c323c999d31cd9bfdd` |
| initial | `Q'` | `7965aadc792ce6e6a4ada3ea51371cc2f3bee8eb015d3047ab33568d3f38fc57` |
| initial | `G'` | `09cc2a0cc7b862703a3f6f576018f6abb3dc21412de43bc2e3b268b9b3d7aa46` |
| initial | `B'` | `aa5f94faced228bb2257180e48865bc427067fbdace2e0ea49205991225a0371` |
| initial | `C'` | `bd4b13650a6518fed669fff2e2245abdcebd9c4a2615b4618669c6acaac181d1` |

## 3. Exact enumeration of both root cosets

The neighbor is the disjoint union

```text
L'=H union ((v/2)+H).
```

For the integral coset, every norm-two vector lies in one original
orthogonal block. Fresh exact reverse-LDL enumeration gives all 240 `E8`
roots and all 72 `E6` roots before applying the parity functional. The
retained block counts are:

| support | block root counts after `H` parity |
|---|---|
| preferred | `112,128,128,128,40,32` |
| initial | `112,112,128,112,72,32` |

Both sums are 568.

For the half coset, write `w=v+2x`. Then

```text
(v/2+x)^T S (v/2+x)=2
  iff
w^T S w=8.
```

Each block enumerator uses an exact rational `LDL^T` factorization. At every
recursion node, the remaining interval is derived by integer `isqrt` after
clearing the exact rational center denominator. There is no coordinate box,
floating-point cutoff, or solver status.

The exact minimum block contributions in the six parity cosets are

```text
preferred: 4,2,2,2,4,2   (sum 16)
initial:   4,4,2,4,0,2   (sum 16).
```

Since both sums already exceed eight, the half coset contains no roots.
The result JSON also retains every block histogram, accepted-node count,
and the final exact norm/parity dynamic program.

The frozen direct 44-dimensional run that exceeded 124 seconds is not used.
It remains `TIMEOUT_NON_EVIDENTIARY` in `failed-runs.md`.

## 4. Preferred all-six-block root system

For the preferred support

```text
{3,6,9,18,25,33,35,41},
```

the complete 568-root system has span rank 43. Its nonorthogonality
components have sizes

```text
2,2,2,2,30,40,112,126,126,126.
```

The verifier does not infer types from counts. It selects a deterministic
generic positive system, defines simple roots as the positive roots not
decomposable into two positive roots, constructs each exact Cartan matrix,
checks its rank and determinant, classifies its Dynkin graph by path or
three-arm lengths, and verifies that every component root is an integral
combination of those simple roots. The resulting types are

```text
A1^4 orthogonal_sum A5 orthogonal_sum D5 orthogonal_sum
D8 orthogonal_sum E7^3.
```

Thus the complete root system has no `A2`, `A6`, `E6`, or `A20` component.
The preferred transformed package therefore evades the already verified
orthogonal-component screens as an abstract `S',Q',G',B',C'` package. This
is not frame compatibility: no 231-row projector frame or Schur-square
origin has been constructed or checked.

The root span has rank 43, so `L'` is not an orthogonal sum of irreducible
ADE root lattices. This is stronger than merely finding a nontrivial
full-rank gluing.

## 5. Preferred primitive closure and `H0/H1`

In original Wave 27 coordinates, let

```text
z=(0^32, 2,1,0,-1,-2,0, 0^6).
```

Fresh coordinate transport verifies that `z` is primitive in `L'`, is
orthogonal to all 43 checked simple roots, and has

```text
z^T S z=z_P^T S' z_P=12,
div_L'(z)=gcd{(z,x):x in L'}=3.
```

Since the root span has codimension one, `z` spans its rational orthogonal
line. Put

```text
R    = lattice generated by all roots,
Rbar = (R tensor Q) intersect L',
K    = Rbar_perp intersect L',
H0   = Rbar/R,
H1   = L'/(Rbar orthogonal_sum K).
```

The checker divides the pairing row `S'z` by its exact gcd three and builds
the full integer kernel from a unit pivot. This proves that the emitted
43-column basis is the saturated lattice `Rbar`, not merely a sublattice.
Direct Gram and coordinate determinants give

```text
K = <12> and is rootless,
det(R)=12288,
det(Rbar)=12,
|H0|=[Rbar:R]=32,
|H1|=[L':Rbar orthogonal_sum K]=4,
[L':R orthogonal_sum K]=128.
```

All bases and Gram matrices are emitted with hashes. In particular,

```text
det(R)*det(K) / (|H0|^2 |H1|^2)
 = 12288*12/(32^2*4^2)
 = 9
 = det(L').
```

This is an explicit realization of both abstract gluing stages in the
separate Wave 28 `H0/H1` dictionary. It remains a hostile arithmetic/lattice
control, not an endpoint-origin certificate.

## 6. Retained initial support

The initially found support

```text
{0,3,11,14,22,28,30,42}
```

is retained after the preferred support, preserving discovery chronology.
Its complete root system is

```text
A1^2 orthogonal_sum A5 orthogonal_sum E6 orthogonal_sum
D8^3 orthogonal_sum E7,
```

with component sizes `2,2,30,72,112,112,112,126`. The roots span rank 44.
The 44 simple roots have Gram determinant 9,216 and determinant 32 in the
emitted `P` basis:

```text
det(root lattice)=9216=9*32^2,
[L':root lattice]=32.
```

This independently confirms the original full-rank gluing cross-control.

## 7. Adversarial replay and defects

The final standard-library suite passes:

```text
Ran 25 tests
OK
```

It attacks input drift, block coverage, neighbor-basis determinant and
inverse, all transformed invariants, direct `B'` parity, direct
`tr((C')^2)`, complete matrix hashes, both cosets, Cartan classification,
the rank-one complement, every `H0/H1` index, the initial index-32 control,
the non-evidentiary timeout, support mutation, basis corruption,
byte-identical regeneration, and every status wall.

One hostile-test assumption was refuted: changing support coordinate 41 to
42 preserves all three scalar neighbor norms. This is retained as a positive
control. The checked negative replacement `41 -> 2` gives `14,14,294`.
This was a test-design defect only; no mathematical or scope defect was
found in either frozen construction.

## 8. Exact status wall

```text
preferred all-six-block abstract hostile control: VERIFIED
preferred H0/H1 realization:                     VERIFIED
initial full-rank index-32 cross-control:         VERIFIED
primitive embedding in Z^231:                    NOT CONSTRUCTED
231-row norm-four projector frame:                NOT CONSTRUCTED
required M alphabet and row profiles:             NOT CONSTRUCTED
Q'=X^T(M o M)X Schur-square origin:               NOT CONSTRUCTED
graph:                                            NOT CONSTRUCTED
n3=708:                                           UNKNOWN
Conway-99 existence:                              UNKNOWN
novelty:                                          UNKNOWN
```
