# Wave 40 rank-equality proof-agent report

```yaml
role: proof_a
date_utc: 2026-07-27
git_commit: 6b28af70c67f062d687251494a047debe70a246f
claim_label: CANDIDATE
scope: conditional exclusion of characteristic-seven ranks at most 21 when n3=4158
method: exact edge-local rank completion, quotient syndromes, and exhaustive finite-field matching censuses
limitations: discovery cannot verify itself; endpoint and ranks 22 through 44 remain open; no general upper-bound or novelty claim
```

## Candidate theorem

At the prism-free endpoint `n3=4158`,

```text
rank_F7(M) >= 22.
```

This is conditional, not an endpoint exclusion.

## Proof outline

For an edge `xy`, let `z` be its triangle mate and let

```text
L={x,y,z} union X union Y
```

be the verified 27-vertex local set. If `B=K[L,L]` for
`K=J-I-2A=N M N^T` over `F_7`, then restricting the full column space to
`L` gives

```text
dim(R/col(B)) <= rank(K)-rank(B).                (1)
```

Every outside vertex has one of exactly 144 patterns when adjacent to `z`,
or 4,356 patterns when nonadjacent to `z`. Its restricted column is the
affine vector `1-2A[L,w]`.

The twelve vertices `Z=N(z)-{x,y}` lie outside `L`, and the `mu=2` equations
force their patterns to form a perfect matching between the twelve points
of `X` and the twelve points of `Y`.

Exact computation then gives:

1. For local type `2+2+2`, `rank(B)=19`. Only 36 of all 4,500 patterns lie
   in `col(B)`, and all have `a_z=0`. This excludes global rank 19.
2. At global rank 20, the `Z` syndromes must lie on one quotient line. The
   144 patterns occupy 66 lines, each containing at most four patterns. This
   excludes rank 20.
3. At global rank 21, a local `2+4` edge would have rank 21, yet none of its
   144 `Z` columns lies in its local column space. If no such edge exists,
   every edge is `2+2+2`; all 1,923 possible quotient two-spaces have
   bipartite matching number at most eight. This excludes rank 21.

As a fail-closed boundary control, 32 of the 25,744 quotient three-spaces do
support a perfect matching. The argument therefore stops at rank 22.

## Status

```text
conditional r7>=22:                  CANDIDATE
endpoint n3=4158 excluded:           NO
general upper bound below 4158:      NOT PROVED
Conway-99 and literature novelty:    UNKNOWN
```
