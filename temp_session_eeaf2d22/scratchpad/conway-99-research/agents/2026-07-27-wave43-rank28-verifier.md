# Wave 43 verifier report: conditional endpoint rank 28

```yaml
role: verifier
date_utc: 2026-07-27T16:13:39Z
git_commit: e28f90464d00b98d37672b0b2b23dba15399a6f2
claim_label: VERIFIED
scope: conditional endpoint n3=4158, all four edge-local types, no completed-graph automorphism
inputs:
  - path: verification/wave41-rank26-secondary/secondary_check.py
    sha256: 3dc38b519712916bc410775c2e8c9d7099bae53268834c92fd06505a9cddb7a3
  - path: verification/wave42-rank27/independent-results.json
    sha256: a207b1bcc267aaefdea704c1173e3ed01a81029507d3bc76aa295caccad03be4
  - path: attempts/wave43-rank28-motif/exact-results.json
    sha256: 8878b40898ba9577ef01fb51ab5631632fb0e6bca3394c594b9c399d51385230
  - path: attempts/wave43-type33-rank2/exact-results.json
    sha256: f9f023a7f5da0b51df1f825c83a2405de16a6e4d5245965332df4ace46e8bd8d
method: independent local-matrix reconstruction, rank-pruned permutation DFS, batched GF(7) elimination, and two separately implemented pivot/mate CSPs
command: see verification/wave43-rank28/run-report.yaml
outputs:
  - path: verification/wave43-rank28/independent-results.json
    sha256: 4e6bc6a04fb65b6dd2a873c9b446d305d65aaca46fecf8703da2886aa1859025
  - path: verification/wave43-rank28/comparison.json
    sha256: 3cc27ac01281d47c238748bda30602fc6fcbe38c19ae48ae073c0f47df5a1f43
limitations: endpoint and Conway-99 remain UNKNOWN
```

## Verdict

**VERIFIED:**

```text
n3=4158  ==>  rank_F7(M)>=28.
```

Equivalently, any hypothetical target with `rank_F7(M)=27` contains at least
one induced triangular prism.

## Independent evidence

The checker imports no Wave 43 discovery implementation. It independently
rebuilds the local graph, transported matrices, border signatures, quotient,
Schur residual, perfect-matching universe, and sample literal 39-point blocks.

The exact even-type outcomes are:

```text
222: 332 bounded-rank derangements,
     3,451,140 labelled pairs, zero rank-27 survivors;
24:  1,352 bounded-rank derangements,
     14,054,040 labelled pairs, zero rank-27 survivors;
6:   288 minimum-rank derangements,
     2,993,760 labelled pairs, zero residuals of rank at most two;
6 higher-F CSP:
     1,014 pivot assignments, 92,274 mate branches,
     488 unary survivors, 1,058 nodes, zero leaves.
```

The independently reconstructed type-`33` CSP visits:

```text
666,666 branches,
491,220 invertible principal pivots,
60,306 unary-surviving branches,
122,922 backtracking nodes,
zero complete leaves.
```

Both CSPs accept separately planted valid leaves in eleven nodes, so their
zero results are not produced by an always-reject bug. Exact comparison has
36/36 matching fields and no discrepancies. Sixteen verifier tests and
fifteen discovery-package tests pass; the full independent deterministic
replay passes.

## Mathematical boundary

At the endpoint the only local types are `222`, `24`, `33`, and `6`, and all
now have local rank at least 28. Principal-block monotonicity and the verified
global rank transport give the displayed theorem.

The endpoint global ceiling is 44, so rank 28 is compatible. This is not an
endpoint exclusion, does not improve the general upper bound `n3<=4158`,
does not construct a graph, and does not resolve Conway-99. Novelty and
priority remain `UNKNOWN`.

See `verification/wave43-rank28/audit.md` for the complete proof and control
audit.
