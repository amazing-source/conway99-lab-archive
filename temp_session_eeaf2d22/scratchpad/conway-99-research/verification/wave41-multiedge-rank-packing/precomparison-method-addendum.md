# Pre-comparison method addendum

Date: 2026-07-27 UTC

This note was written before opening, importing, or running the Wave 41
discovery package.

The protocol freeze proposed enumerating the perfect matchings supported by
`H^T U=0`.  The independent calculation found that, for every all-odd type,
all 144 individual border columns already satisfy this condition.  A literal
enumeration would therefore be the irrelevant full set of `12!` permutations.

The verifier replaces that step by the next necessary equality condition.
When `S X=U`, exact singular Schur elimination gives

```text
rank(K39)=25+rank(W-U^T X).
```

Rank 25 requires `W-U^T X=0`.  Since every legal internal-fibre block `W`
has zero diagonal, a selected pair `(i,j)` can occur only when

```text
border(i,j)^T S^- border(i,j)=0.
```

This defines an explicit bipartite graph on twelve `X` labels and twelve `Y`
labels.  The verifier computes a maximum matching and a same-cardinality
minimum vertex-cover certificate.  If its matching number is below twelve,
Hall's obstruction excludes all `12!` permutations at once.  If its matching
number is twelve, the verifier enumerates every perfect matching of this
smaller graph and checks the entire residual target against the exact legal
perfect-matching form of `W`.

This is a proof-preserving compression, not a restricted search: every
rank-25 completion must pass the diagonal condition.
