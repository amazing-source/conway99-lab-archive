# Wave 46 verifier: characteristic-seven projector code

```yaml
role: verifier
date_utc: 2026-07-27T17:32:00Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: >
  Conditional F7 derivations and all generic rank-28-through-44 controls;
  null endpoint status retained.
```

## Verified result

The clean-room implementation was frozen before discovery inspection.
Conditional on the endpoint projector identities, it verifies:

```text
C subset C^perp and C subset 1^perp,
d(C^perp)>=3,
A69>=1386,
excluded congruence weights exactly 1,2,4,
C^(o3)=F7^231,
r7>=11.
```

The six endpoint scalar compositions are distinct. All 56 nonconstant
degree-one and ordered degree-two complete-enumerator moments have strict
slack at rank 28. The conventional falling-moment minimum second slack is
`498756830339225186222981718`.

The verifier independently rebuilt all 17 archived positive controls for
`r=28,...,44`. Every generator has exact rank, zero row sums, zero Gram
matrix, and 231 projectively distinct columns. Every projection and
generator-column-stream hash matches. The local enumerator and inherited
`A69>=668653683264` also reproduce exactly.

None of the control generator rows or their nonzero scalar multiples matches
one of the six endpoint compositions. This confirms the intended separation:
they are valid generic codes, not endpoint projector candidates.

The `A+3I` prompt object is independently verified as an invertible `99 x 99`
matrix over `F7` with determinant three. It is different from the
`231 x 231` projector and remains quarantined from every live conclusion.

## Status wall

```text
scoped algebra and controls:               VERIFIED
ordinary-enumerator contradiction:         NONE
degree-two complete-enumerator conflict:   NONE
new endpoint rank floor:                    NONE
endpoint n3=4158:                           UNKNOWN
strict upper bound below 4158:              NOT PROVED
Conway-99 and novelty:                      UNKNOWN.
```

The next useful coding-theory step must retain the geometry of the 231
distinguished projector rows: pairwise row-sum compositions, character sums,
higher complete MacWilliams data, or exact identities among their mutual
Schur products.
