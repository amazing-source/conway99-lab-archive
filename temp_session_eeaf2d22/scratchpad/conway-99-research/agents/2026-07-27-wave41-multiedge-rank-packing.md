# Wave 41 multi-edge rank packing

```yaml
role: proof_a
date_utc: 2026-07-27T05:02:46Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: CANDIDATE
scope: >
  A scoped characteristic-seven strengthening for all-odd edge types and an
  exact obstruction to naive packing of overlapping triangle blocks.
method: >
  Full three-fibre Schur reduction, finite diagonal-isotropy exhaustion,
  exact SRG polynomial algebra, and low-rank local controls.
limitations:
  - The seven even-part edge types remain unresolved.
  - Discovery cannot verify its own rank-26 implication.
  - No universal rank improvement, endpoint exclusion, or upper-bound improvement is claimed.
  - Novelty and priority remain UNKNOWN.
```

## Result

Starting from the Wave 40 identity

```text
rank_F7(K39)=1+rank_F7(3I-A_core),
```

eliminating the first twelve-point matching fibre gives

```text
H = [ P+Q       F+(3I+P) ]
    [ F^T+(3I+P)   P+R   ].
```

For the four types in which every alternating part of `(P,Q)` is odd,
`P+Q` is invertible. Rank 25 would force the Schur identity

```text
P+R=(F^T+3I+P)(P+Q)^(-1)(F+3I+P).
```

The exact checker exhausts all 576 column/preimage quadratic-form tests.
Types `1^6`, `1^3+3`, and `1+5` have an impossible column. Type `3+3`
has one forced permutation, whose forced `R` contains values two and three
rather than a zero-one perfect matching. The candidate scoped conclusion is

```text
all-odd edge type => rank_F7(K39)>=26 => rank_F7(M)>=26.
```

No claim is made for the seven even-part types.

## Structural obstruction to block packing

For every graph vertex `v`,

```text
h_v=(A+4I)e_v
```

is a global mod-seven kernel vector because

```text
(J-I-2A)(A+4I)=14J-7A-28I.
```

If `v` belongs to a triangle `T`, this vector is supported inside the
39-point block attached to `T`. The three such vectors for `v in T` are
independent and are killed by all 60 outside columns. Thus, for a block
kernel basis `H` and border `U`,

```text
dim ker(H^T U)>=3.
```

This refutes the hoped-for full-rank border projection and explains why
nominal ranks of overlapping triangle blocks cannot simply be added. The
directions are globally repeated vertex-star columns, not independent local
defects.

## Exact controls and frontier

The package retains:

- a fully specified generic core with component sizes `12+12+12`,
  Laplacian nullity nine, and `rank_F7(K39)=28`;
- a fully specified triangle-free core with component sizes `18+18`,
  Laplacian nullity eight, and `rank_F7(K39)=29`; and
- the seven-independent-star 49-triangle block as an open compatibility
  target rather than a result.

Ten standard-library tests pass, and `exact-results.json` regenerates byte
for byte. Full proofs, controls, failed routes, and the status wall are in
`attempts/wave41-multiedge-rank-packing/`.
