# Independent Wave 58 cross-incidence rank audit

Verdict: `VERIFIED` in the stated conditional and normalized scope.

The Gram identities, prior Wave 36 rank/multiplicity replay, universal
`C4(X)<=27` bound, normalized `m=4` and `m=6` component censuses,
component-specific four-cycle conclusions, three surviving rows, separate
local/scalar controls, and restricted Wave 40 lift replay were independently
reproduced.

No hidden completed-graph automorphism was used.  The endpoint and Conway-99
remain `UNKNOWN`.

## Clean-room boundary

The verifier froze its protocol and hashes for `AGENTS.md`, the verified
Wave 36 block package, and the verified-scoped Wave 40 edge-coupling package
before inspecting Wave 58.  The sealed discovery package was then hashed
separately.  The implementation imports no discovery code and uses
standard-library exact arithmetic and bounded exhaustive enumeration.

## 1. Cross-incidence Gram identities

Order the putative endpoint graph as `T|X|Y`, where `X` has three
twelve-vertex fibres and `Y` has 60 vertices.  Let `B` be the `36 x 60`
`X/Y` incidence matrix, `A_X` the cubic graph on `X`, and `A_Y` the
8-regular graph on `Y`.

Entrywise common-neighbor counting verifies

```text
B^T B = 12I-A_Y+2J-A_Y^2,

B B^T = 12I-A_X+2J-blockdiag(J12,J12,J12)-A_X^2.
```

The diagonals are respectively `12+2-8=6` and
`12+2-1-3=10`, matching the column and row weights of `B`.  For two
distinct `X` vertices, the block-diagonal term removes their common fixed
triangle vertex exactly when they lie in the same fibre.  No entry-case
error was found.

On the 33-dimensional subspace orthogonal to all three fibre indicators,
both `J` terms vanish and the second identity factors as

```text
B B^T=(3I-A_X)(4I+A_X).
```

## 2. Wave 36 chronology and rank replay

This rank theorem is prior `VERIFIED` Wave 36 work, not Wave 58 novelty.  If
`kappa` is the number of components of `A_X`, then the two fibre-constant
sum-zero vectors lie in `ker(B^T)`, and the remaining kernel directions are
the `kappa-1` eigenvalue-3 directions of `A_X` orthogonal to the fibre
indicators.  Cubicity puts the spectrum of `A_X` in `[-3,3]`, so `-4`
cannot create another zero in the factorization.  Hence

```text
dim ker(B^T)=kappa+1,
rank(B)=35-kappa,
dim ker(B)=25+kappa.
```

On `ker(B)`, the first Gram identity gives

```text
(A_Y^2+A_Y-12I)v=0.
```

If `a=mult_Y(3)` and `b=mult_Y(-4)`, exact dimension and trace equations are

```text
a+b=25+kappa,
3a-4b=26-4kappa.
```

Therefore

```text
a=18,
b=7+kappa.
```

Wave 36 component balance had already proved the possible component-unit
partitions

```text
[12], [4,8], [6,6], [4,4,4].
```

Thus `kappa` is 1, 2, or 3, and the only project-live rows are

```text
(a,b,kappa,rank(B))
=(18,8,1,34),
 (18,9,2,33),
 (18,10,3,32).
```

## 3. Universal four-cycle bound

Every vertex of the cubic triangle-free `X` graph supplies three unordered
neighbor pairs, hence there are `36*3=108` wedges.  The endpoints of each
wedge are nonadjacent.  In the ambient SRG they have exactly two common
neighbors; the wedge center is already one, so at most one other common
neighbor can close the wedge to a four-cycle.  Each four-cycle contains four
wedges.  Therefore

```text
4 C4(X) <= 108,
C4(X) <= 27.
```

This is a universal upper bound.  It does not assert that 27 is attainable
in any of the component lanes.

## 4. Coordinate-normalized component enumeration

For one component with `m` vertices in each fibre, independently relabel the
three fibre coordinates so that:

- the fibre-zero internal matching is fixed;
- the `0/1` and `0/2` cross matchings are identity.

The remaining data are the internal matchings in fibres one and two and the
`1/2` cross permutation.  This normalization is complete because it is only a
choice of coordinates.  It does not require the relabelling to extend to an
automorphism of the completed graph.

The raw normalized presentation counts are

```text
((m-1)!!)^2 m!,
```

giving 216 for `m=4` and 162,000 for `m=6`.  These are not numbers of graph
isomorphism classes; residual coordinate stabilizers can identify multiple
presentations.

The independent enumerator requires connectedness, cubicity,
triangle-freeness, and `X`-nonedge codegree at most two.  It reproduces:

```text
m=4:
  raw 216, accepted 50,
  C4 distribution {2:6, 4:30, 6:14}.

m=6:
  raw 162000, accepted 34640,
  C4 distribution
  {0:288, 1:576, 2:3744, 3:6744, 4:11520,
   5:7128, 6:3648, 7:936, 9:56}.
```

Every stored first witness for every cycle value was reconstructed and checked
for degree, connectedness, triangle count, codegree, and four-cycle count.
The discovery field name `canonical_witness_by_C4` means the deterministic
first normalized witness, not a canonical graph-isomorphism representative.

## 5. Exact sets versus bounds

The `m=4` and `m=6` component supports imply:

```text
kappa=3, partition [4,4,4]:
  exact local C4 set {6,8,10,12,14,16,18}.

kappa=2, partition [6,6]:
  exact local C4 set {0,1,...,16,18}.
```

The value 17 is absent from the second exact set.

For partition `[4,8]`, only the `m=4` component is enumerated.  It contributes
2, 4, or 6 cycles; the unenumerated 24-vertex `m=8` component has the wedge
upper bound 18.  Therefore

```text
2 <= C4(X) <= 24
```

is a bound, not an exact attainable interval.  Combining the two `kappa=2`
partitions gives the valid overall bound

```text
0 <= C4(X) <= 24,
```

but Wave 58 does not prove that every integer in this interval is attainable.
Likewise `0<=C4(X)<=27` for `kappa=1` is only a bound.

## 6. Local and scalar controls

All three surviving rows retain scoped failure-of-obstruction controls:

- `kappa=1`: the prior verified Wave 36 connected core has `C4(X)=0` and
  Gram rank 34; the `(18,8,0)` residual scalar moments check.
- `kappa=2`: two independently reconstructed `m=6`, zero-cycle components
  give component sizes `[18,18]`, and the `(18,9,0)` scalar moments check.
- `kappa=3`: three `m=4`, four-cycle components give sizes `[12,12,12]`
  and total `C4(X)=12`; root multiplicities `(5,6,8,1,9,2)` on
  `(-3,-2,-1,0,1,2)` give exact residual power sums
  `(31,-22,94,-166,550)`.

The edge-list hashes of both constructed local controls were independently
reproduced.  These `A_X` graphs and residual scalar spectra are separate
objects.  They do not supply the same binary matrix `B`, a compatible
`A_Y`, or an endpoint graph.

## 7. Restricted Wave 40 replay

The verifier independently rebuilt the named rank-11 quotient from the prior
Wave 40 verified artifact and visited all `2^18=262,144` endpoint masks.
Exactly 37,378 are triangle-free.  Every accepted lift has component profile
`[12,24]`, and the exact four-cycle distribution is

```text
{4:1944, 5:4320, 6:7560, 7:7008, 8:8172,
 9:3504, 10:3696, 11:480, 12:658, 14:36}.
```

Thus 13 is absent; `4<=C4(X)<=14` records only the minimum and maximum, not a
filled interval.

This replay concerns one of the eight normalized rank-11 quotients and
retains the joint `all-222` and `r3=12` assumptions.  It is a positive
restricted `kappa=2` control, not an enumeration of all endpoint cores and
not evidence against `kappa=1` or `kappa=3`.

## Reproduction

```powershell
python -B verification\wave58-cross-incidence-rank\independent_check.py
python -B verification\wave58-cross-incidence-rank\independent_check.py `
  --verify verification\wave58-cross-incidence-rank\independent-results.json
python -B -m unittest discover `
  -s verification\wave58-cross-incidence-rank -p "test_*.py" -v
```

Fourteen verifier tests cover the baseline, both component distributions,
exact-set versus bound wording, the restricted Wave 40 support, Gram and rank
mutations, component-count and witness mutations, scalar corruption,
chronology corruption, and status inflation.

## Final classification

```text
cross-incidence Gram identities:                   VERIFIED, conditional
Wave36 rank/component/multiplicity replay:          VERIFIED prior work
C4(X)<=27:                                         VERIFIED upper bound
normalized m=4 census 216 -> 50:                   VERIFIED exact scope
normalized m=6 census 162000 -> 34640:             VERIFIED exact scope
kappa=3 local C4 set:                              VERIFIED exact local set
kappa=2 [6,6] local C4 set:                        VERIFIED exact local set
kappa=2 [4,8] and overall ranges:                  VERIFIED as bounds only
three separate local/scalar controls:              VERIFIED scoped
one-quotient Wave40 replay 262144 -> 37378:         VERIFIED scoped
simultaneous B and compatible A_Y:                 UNKNOWN
endpoint exclusion/construction, Conway-99:         UNKNOWN
novelty:                                            UNKNOWN
```
