# Wave 27 A2-summand-free construction: failed and restricted routes

## Status wall

This ledger accompanies a positive hostile control.  It is not a
classification and does not turn any failed search into nonexistence
evidence.  The exact control is only an abstract coupled
`(S,Q,G,B,C)` arithmetic/lattice package.  It has no certified primitive
embedding, 231-row projector frame, Schur-square origin, graph, or target
realization.

## 1. The old rank-four tail

The most immediate determinant-nine decomposition,

```text
E8^5 orthogonal_sum A2^2,
```

is the frozen Wave 24 hostile control and is rejected by the verified Wave
26 projector-frame obstruction if one tries to add the required 231-row
origin.  No classification of even positive-definite rank-four
determinant-nine forms was attempted here.  In particular, failure to find
another rank-four tail was not used as evidence.

The successful construction instead uses

```text
S = E8^4 orthogonal_sum E6^2.
```

It contains embedded `A2` root subsystems, but its complete root-component
certificate shows that it has no **orthogonal `A2` direct summand**.  This
distinction is essential.

## 2. Naive `Q=S` fails

For the displayed `S`, setting `Q=S` gives

```text
tr(SQ)=tr(S^2)=252,
```

not the endpoint value `60`.  Thus the lattice-only candidate does not
automatically extend to the coupled identities.

The successful `Q` uses `E8^-1` on each `E8` block and a rank-one
projector construction on each `E6` block.  No claim that this is the only
choice is made.

## 3. Coordinate-convention mismatch

Two isomorphic `E6` Dynkin coordinate conventions appeared during the
discovery exchange.  This package freezes diagonal two with edges

```text
(0,1), (1,2), (2,3), (3,4), (2,5).
```

In this convention the selected sign-canonical seed is

```text
v=(1,0,-1,0,0,1),
v^T E6^-1 v=4/3.
```

Blindly reusing the vector `(1,1,0,-1,0,0)` from the other coordinate
ordering gives norm `10/3` and does not reproduce the integral package.
The hostile test retains this mismatch so a future relabeling cannot pass
silently.

## 4. Bounded seed scan

The reproducible discovery scan is complete only under all of these
restrictions:

- the displayed `E6` coordinate matrix is fixed;
- `v` lies in `{-1,0,1}^6`;
- `v` and `-v` are identified;
- `P=v(v^T E6^-1)/(v^T E6^-1 v)`;
- `B6=I+8P` and `Q6=E6^-1 B6`;
- the full `Q` is block diagonal;
- the same `E6` block is repeated twice; and
- no automorphism of a target is assumed.

Exactly 27 sign-canonical seeds survive inside that finite box.  Their
complete list is in `exact-results.json`.  The count is not a
classification of seeds outside the box, cross-block `Q`, determinant-nine
forms, embeddings, projectors, or graphs.

## 5. Cross-block and projector searches not performed

No cross-block entries of `Q` were searched because the explicit
block-diagonal witness already satisfies every scoped coupled identity.
No absence claim is attached to this omission.

Likewise, this construction does not search for the 231 norm-four rows or
the cubic tensor required by a Schur-square origin.  A separate cubic-tensor
scout may obstruct such an extension; that work is outside this
construction certificate and is not imported as a premise.

## 6. Retained test failure

The first local unit-test run had one bookkeeping failure:

```text
expected tr(S^2)=260
exact checker returned 252
```

The mistaken mental count treated the `E8` Dynkin diagram as having eight
edges.  The frozen `E8` matrix has seven edges, so each block contributes
`32+2*7=46`, and

```text
4*46 + 2*34 = 252.
```

The test expectation was corrected to `252`.  No construction matrix or
mathematical conclusion changed.  The subsequent 15-test run passed.
