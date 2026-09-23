# Wave 42 rank-27 clean-room verifier protocol freeze

Date frozen: 2026-07-27 UTC

Role: independent verifier.

## Access boundary

This protocol was fixed before opening, importing, or executing any file under
`attempts/wave42-rank26-equality/**` or
`agents/2026-07-27-wave42-rank26-equality.md`.  The only mathematical and
implementation inputs admitted before the precomparison freeze are the
independently verified Wave 39--41 artifacts listed in
`input-freeze.sha256`.

No automorphism of a completed graph is assumed.  Relabelling the three
twelve-point fibres merely chooses coordinates: the remaining border is
always enumerated as a labelled permutation and the third-fibre relation as
one of all `(11)!!=10,395` labelled perfect matchings.

## Exact target

Independently decide whether every hypothetical `srg(99,14,1,2)` satisfies

```text
rank_F7(M) >= 27.
```

The verifier must cover all eleven positive partitions of six.  It may
promote the theorem only after a complete exact exclusion of rank 26 in
every type and replayable hostile tests.

## Rank reduction fixed before comparison

For the singular symmetric block

```text
K39 = [[S,U],[U^T,W_R]]
```

over `F_7`, let the rows of `H` span `ker(S)`, put `F=HU`, let the columns
of `Z` span `ker(F)`, solve `SX=UZ`, and set `T=Z^T U^T X`.  Exact
congruence splits `2 rank(F)` hyperbolic directions and leaves

```text
rank(K39)
  = rank(S) + 2 rank(F) + rank(Z^T W_R Z - T).       (1)
```

For a local type with `e` even parts, the verified inputs give
`rank(S)=25-2e` and `rank(F)>=e`.  Wave 41 excludes rank 25.  Consequently

```text
rank(K39)=26
iff
rank(F)=e and rank(Z^T W_R Z-T)=1.                   (2)
```

The rank-at-most-one predicate used in every search is exact: a symmetric
matrix `D` over an odd field has rank at most one iff all of its two-by-two
minors vanish.  Equivalently, either `D=0`, or for a nonzero diagonal pivot
`D[p,p]`, every entry satisfies
`D[i,j]D[p,p]=D[i,p]D[j,p]`.  A nonzero symmetric rank-one matrix always
has a nonzero diagonal, so this pivot test is complete.

## Seven even-part types

For each even-part type the implementation will independently:

1. regenerate every observed projective border-signature line;
2. enumerate every dimension-`e` span and every supported labelled
   bipartite perfect matching;
3. verify directly that each emitted permutation has `rank(F)=e`;
4. enumerate all 10,395 labelled `R` for every emitted permutation;
5. apply the exact rank-at-most-one predicate to every residual;
6. retain explicit counters and hashes proving complete pair coverage.

Vectorized integer arithmetic may batch cases, but every field operation is
reduced modulo seven and no floating-point rank computation is permitted.
Positive controls include synthetic rank-zero and rank-one residuals; hostile
controls include a rank-two residual with every diagonal zero, which defeats
an invalid diagonal-only test.

## Four all-odd types

For `e=0`, `F=0` is necessary.  The implementation will use a complete
pivot-CSP/backtracking formulation over the twelve labelled border choices
and the six edges of `R`, rather than iterating `12!*10,395` pairs.

For each possible rank-one pivot coordinate and field value, the equations
`W_R-U^T S^- U = vv^T/lambda` are imposed entry by entry.  The search state
tracks:

- the partial border bijection;
- the partial perfect matching `R`;
- the chosen pivot column and its twelve residual pivot entries;
- every forced two-by-two-minor equation;
- unused right labels and unmatched third-fibre vertices.

The branching order is deterministic minimum-remaining-values.  A branch is
closed only by an exact field contradiction, bijection collision, matching
collision, or completion checked by dense rank.  A coverage recurrence will
sum the number of represented labelled `(permutation,R)` pairs at every
closed node, and must equal

```text
12! * 10,395 = 4,979,221,632,000
```

per all-odd type, hence `19,916,886,528,000` across the four types.  (The
verifier records and checks this arithmetic itself; any competing reported
coverage total is treated as a comparison field, not as a premise.)

Positive controls inject a target made from a legal matching plus a
rank-one matrix and must be found.  Hostile controls mutate one off-diagonal
entry to create rank two and must be rejected.  The CSP is also cross-checked
against brute force on reduced labelled universes.

## Promotion and scope wall

The verifier labels the universal rank-27 theorem `VERIFIED` only if:

- the checker and hostile tests are frozen before discovery comparison;
- all eleven labelled types have complete exact coverage;
- all direct decomposition checks and rank-one controls pass;
- the preliminary result replays byte-for-byte;
- post-freeze comparison finds no mathematical discrepancy.

Even a verified rank-27 floor does not construct a 99-vertex graph, exclude
`n3=4158`, improve `n3<=4158`, settle Conway-99 existence, or establish
literature novelty or priority.  Those fields remain `UNKNOWN` or
`NOT PROVED`.
