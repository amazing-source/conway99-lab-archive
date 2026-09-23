# Wave 205 integration audit

## Verdict

`PASS_SCOPED_INFLECTION`.

Wave 205 reaches an independently verified stopping point for the proposed
pair-local fourth-order route.  It derives exact nonedge two-star constraints,
exhausts the first two possible integer trace-count levels, and proves with
full-rank local controls that the checked pair data do not determine the
fourth trace.  It also factors the full fourth-trace matrix through a
graph-specific crossing kernel and proves that the tempting incidence-rank,
first-moment, and ambient-dimension shortcuts do not supply a contradiction.

This is an obstruction and route-selection result.  It does not classify the
actual nonedge fourth traces of an endpoint, exclude rank 11, exclude
`n3=4158`, improve the rigorous interval, construct a graph, or resolve
Conway 99.

## Frozen boundary

```text
Conway-99:                 UNKNOWN
rank-11 endpoint:          UNKNOWN
n3=4158 endpoint:          UNKNOWN
rigorous n3 interval:      708<=n3<=4158
conditional Q bound:       Q>=7059
Q>=7060:                   NOT PROVED
automorphism assumption:   NONE
```

The Wave 205 protocol was frozen at
`attempts/wave205-fourth-trace-globalization/protocol.md` before discovery
work was integrated.

## Nonedge pair-local theorem

For a nonedge `xy`, label the two common-neighbor triangles first in both
seven-block stars.  The verified integer cross Gram has

```text
marked corner:       [[1,2],[2,1]]
marked row/column:   0^0 1^5 2^2
ordinary total:      6
```

If `t_xy` is the number of entries equal to two, then

```text
t_xy>=6,
average_(y nonadjacent to x) t_xy=7,
tr(P_xP_y)=2t_xy in F_3,
h_xy=tr((C C^T)^2).
```

An independent normalized enumeration of the complete `t=6` and `t=7`
frontier gives:

| `t` | normalized matrices | admissible `h=0` | `h=1` | `h=2` |
|---:|---:|---:|---:|---:|
| 6 | 646 | 0 | 18 | 0 |
| 7 | 7,886 | 297 | 324 | 144 |

Here admissibility means union-Gram rank 11, nonsquare discriminant two, and
true-relation distance at least four.  Four explicit 28-vertex local
certificates realize `t6_h1` and `t7_h0/h1/h2`.  At full ambient rank, and
only there, the verifier identifies the Gram kernel with the true relation
code.

Consequently the following implications are `REFUTED_WITH_SCOPE`:

```text
local projectivity and relation distance force t_xy>=7;
fixed t_xy=7 plus the checked pair data determine h_xy.
```

The certificates are locally consistent two-center balls, not 99-vertex
graphs.  Their unsaturated pairs have not been simultaneously completed.

## Full-matrix factorization and globalization boundary

For ordered triangle-block pairs define

```text
u_x[(T,U)]=B[x,T]B[x,U],
K_D[(T,U),(R,S)]=D[T,R]D[R,U]D[U,S]D[S,T].
```

The full fourth-trace matrix satisfies the verified identity

```text
H=U K_D U^T.
```

Any two distinct blocks through a point `x` give a column of `U` equal to
`e_x`, so

```text
rank_F3(U)=99.
```

Thus the star-pair feature itself supplies no rank loss.  With

```text
Q=B^T B,
M_x=D S_x D,
w_TU=B(D_T o D_U),
```

the verified graph-specific contractions are

```text
(H 1)_x=tr((Q o M_x)M_x),
(K_D vec(Q))_(T,U)=w_TU^T w_TU.
```

The correct fourth-order coordinate caps are 2,145 for the quadratic
trace-zero projector feature, 1,539 for trace-zero self-adjoint operators on
`wedge^2 V`, and 2,210 for the symmetric-square analogue.  All exceed 99.
In particular, `wedge^2(P_x)` is an operator on a 55-space, not a
55-coordinate vector.

An exact 99-label projector control verifies

```text
sum_x P_x=0
but
H 1 != 0.
```

It repeats projector labels and has no target incidence, so it refutes only
the generic first-moment implication.

## Stronger relaxed control

The hostile lane supplies two exact systems with:

- 99 rank-six trace-zero projectors in the nonsquare 11-space;
- 231 labelled singular columns and rank-11 square-zero centered Grams;
- a linear `99 by 231` triple incidence with degrees seven and three;
- a simple 14-regular point graph;
- exact star/projector coupling;
- the same full pair-trace matrix; and
- identical fourth traces on all 693 graph edges.

Their fourth traces differ on 3,888 ordered nonedges.  This stronger
construction-level control still has only 21 projective directions, graph
components `27+36+36`, 1,098 extra triangles, edge common-neighbor counts
`4..9`, and nonconstant nonedge common-neighbor counts including zero.  It is
not strongly regular and is not an endpoint configuration.

## Independent verification

The verifier sealed a source-blind implementation before opening any Wave 205
discovery package:

```text
verification/wave205-fourth-trace-globalization-verifier/SOURCE_BLIND_FREEZE.sha256
sha256 f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853
```

After source exposure, a separate checker imported no discovery Python and
reconstructed the finite censuses and submitted certificates.  Root replay
obtained:

```text
source-blind tests:             9/9 PASS
post-source independent tests:  8/8 PASS
Proof-A submitted tests:       13/13 PASS
Proof-B submitted tests:       12/12 PASS
hostile submitted tests:         6/6 PASS
mathematical/scope findings:      NONE
```

Verifier package:

```text
verification/wave205-fourth-trace-globalization-verifier/package-manifest.sha256
sha256 b93f65f72db94539c7d42d7eca6debbaf3a5c4a401db3b812a80549bcb9b8325
```

## Inflection and next exact theorem

The pair-local fourth-order route is now closed under all premises checked in
Wave 205.  Pair trace, intersection dimension, exact two-center SRG geometry,
the prism-free crossing cap, local rank-11 projectivity, relation distance,
and even the exact average value `t_xy=7` do not determine `h_xy`.

The next useful theorem must impose simultaneous global extension
compatibility across overlapping two-center balls.  Equivalent concrete
targets are:

```text
classify K_D restricted to row(U);
classify Q o (D S_x D);
classify the norms and overlap laws of w_TU=B(D_T o D_U);
derive a three-center consistency law for unsaturated local pairs.
```

Until one of those graph-specific invariants is controlled, fourth-order
trace calculations cannot yield an endpoint contradiction.
