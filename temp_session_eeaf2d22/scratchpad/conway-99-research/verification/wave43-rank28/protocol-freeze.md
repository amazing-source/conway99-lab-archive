# Wave 43 rank-28 verifier protocol

Frozen: 2026-07-27T15:51:19Z

This verifier is not blind to the discovery counts: the assignment supplied
the discovery packages and requested exact-count comparison. Independence
therefore comes from a separate implementation and different search
structure, not from ignorance of the proposed answer.

## Frozen claims

Conditional on `n3=4158`, the endpoint edge types are `222`, `24`, `33`, and
`6`, and the cross-fibre permutation is a derangement. For an edge type with
`e` even parts, the verified input formula is

```text
rank(K39) = (25-2e) + 2 rank(F) + rank(D),  rank(F)>=e.
```

The even-type discovery claims that neither rank-27 mechanism

```text
rank(F)=e,   rank(D)=2
rank(F)=e+1, rank(D)=0
```

occurs for types `222`, `24`, or `6`. The separate type-`33` discovery
claims that its only rank-27 mechanism, `rank(D)=2`, is also absent.

## Independent method

1. Reimplement the local 27-point graph, transported matrix, border columns,
   finite-field row reduction, quotient, perfect-matching matrices, and Schur
   residual without importing either Wave 43 discovery checker.
2. Derive the two rank-27 mechanisms arithmetically and reject hostile
   mutations of the formula.
3. Enumerate endpoint derangements of bounded `F` rank by direct
   rank-pruned permutation backtracking. This is structurally different from
   the discovery generated-projective-subspace cover.
4. For types `222` and `24`, enumerate every rank-`e+1` derangement and test
   all 10,395 labelled perfect matchings for zero residual.
5. For type `6`, enumerate all minimum-rank endpoint derangements, test every
   matching by a batched exact Gaussian rank computation, and independently
   reconstruct the rank-two-`F` zero-residual CSP using literal kernel
   vectors rather than the discovery's expanded equations.
6. Add positive controls for bounded-rank enumeration, matching-form equality,
   batched rank at most two, and a planted zero-residual CSP leaf. Add hostile
   derangement, matching-degree, and rank-formula controls.
7. Compare all invariant counts and complete permutation-stream hashes only
   after the independent result is frozen.
8. Separately reconstruct type `33` with the generic principal-pivot Schur
   equations. Promote the combined endpoint rank-28 theorem only if this
   second lane also closes independently.

## Resource and status rules

- One foreground Python process only; no background workers.
- Sample physical memory during every large loop and abort before free memory
  falls below 15%.
- A timeout, solver exit, or absent found witness is not evidence.
- `VERIFIED` requires complete coverage plus positive controls and exact
  comparison.
- The result, even if verified, is conditional on `n3=4158` and is not an
  endpoint contradiction, a strict general upper bound, a graph, a Conway-99
  solution, or a novelty claim.

