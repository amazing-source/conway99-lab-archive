# Wave 41 construction B: all rank-eleven quotient lifts

```yaml
role: construction
date_utc: 2026-07-27T04:43:20Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: CANDIDATE
scope: "All normalized rank-eleven all-222 quotients and their complete one-triangle endpoint-pairing lift spaces"
inputs:
  - "attempts/wave41-allquotient-lifts/input-freeze.sha256"
method: "Exact quotient isomorphism, affine F2 mask transport, complete Boolean mask enumeration, and exact F7 rank"
command:
  - ".\\.venv\\Scripts\\python.exe -B attempts\\wave41-allquotient-lifts\\exact_check.py --verify attempts\\wave41-allquotient-lifts\\exact-results.json"
outputs:
  - "attempts/wave41-allquotient-lifts/exact-results.json"
limitations: "A one-triangle lift is not a graph completion; the candidate requires independent verification."
```

## Strongest exact candidate

All eight normalized rank-eleven all-`222` triangle quotients are one
fibre-preserving coloured isomorphism class. The checker supplies an exact
vertex map and induced affine bijection of the eighteen endpoint-pairing
bits for every record.

All eight complete lift spaces have the identical exact census:

```text
triangle-free lifts:                 37,378
rank_F7(K39)=33:                        264
rank_F7(K39)=34:                      7,348
rank_F7(K39)=35:                     29,766
```

Consequently, under the joint hypotheses

```text
n3=4158, r3=12, and every edge has type 222,
```

every base-triangle `K39` block has rank at least 33. Thus `r7>=33`, and
the existing parity condition sharpens this joint branch to even `r7>=34`.
This is a **CANDIDATE**, not a self-verified theorem.

## Full quotient census extension

All 4,050 normalized all-`222` quotient forms were assigned their exact
number of triangle-free pairing masks. The count ranges from 10,648 to
262,144. Every form has a local triangle-free lift, so this extension does
not force a prism. Nineteen quotient forms have no quotient triangles and
admit every pairing mask.

## Exact certification design

The canonical quotient is exhaustively ranked over all `2^18` masks.
For each of the eight source records, the checker:

1. verifies a fibre-preserving quotient graph isomorphism;
2. derives the induced affine permutation-plus-constant map on `F_2^18`;
3. checks triangle-free membership for every source mask against its image;
4. transports the exact rank through graph isomorphism;
5. reconstructs and densely reranks a source-side minimum witness.

Thus this is not an assumption that the eight labelled records behave the
same. The equivalence and all source mask spaces are machine checked.

## Honest boundary

The surviving 36-vertex cores do not include the sixty outside vertices.
They do not solve the balanced binary Gram factorization, compatible
eight-regular outside graph, or overlap constraints among the 231 base
triangles. No endpoint exclusion or improved upper bound follows.

The naive rank-33 border route is a documented failure. Every `K39` has
three independent fibre-star kernel vectors. Each automatically annihilates
every outside column because that column is nonadjacent to `T` and selects
two vertices in each fibre:

```text
(4+1+1)+(10-2)=14=0 mod 7.
```

Thus at rank 33, `rank(H^T U)<=3` automatically; the rank-ceiling
requirement `<=5` is vacuous. Continuation must exploit the simultaneous
binary `B`, outside `H`, full `K^2=0`, or overlap compatibility rather than
raw border rank.
