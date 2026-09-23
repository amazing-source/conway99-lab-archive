# Wave 43 Proof Agent A: endpoint rank-28 motif boundary

```yaml
role: proof_a
date_utc: 2026-07-27T15:45:26Z
git_commit: e28f90464d00b98d37672b0b2b23dba15399a6f2
claim_label: DERIVED
scope: >
  Complete rank-27 equality exclusion for endpoint even edge types 222, 24,
  and 6; hostile review of the separate type-33 discovery; candidate combined
  endpoint rank-28 theorem pending independent verification.
```

## Strongest result

Under the conditional prism-free endpoint `n3=4158`, every edge of type
`222`, `24`, or `6` has

```text
rank_F7(K39)>=28.
```

The exact rank-27 dichotomy is

```text
rank(F)=e,   rank(D)=2;
rank(F)=e+1, rank(D)=0.
```

Both mechanisms were exhaustively excluded for the three even types:

```text
type 222 rank-4 derangements:       332
type 222 labelled R checks:     3451140
type 24 rank-3 derangements:       1352
type 24 labelled R checks:      14054040
type 6 minimum-F/R checks:       2993760
type 6 higher-F mate branches:     92274
rank-27 survivors:                     0.
```

The discovery result SHA-256 is
`8878b40898ba9577ef01fb51ab5631632fb0e6bca3394c594b9c399d51385230`.
Nine focused tests pass.

## Type-`3+3` hostile review

The separate `attempts/wave43-type33-rank2/` package covers the remaining
all-odd endpoint type. I checked its principal-pivot lemma, pivot-mate
partition, Schur equations, matching-degree rollback, derangement scope, and
all-different cover. I also independently checked the frozen interaction
table on every compatible assignment pair and found zero asymmetries, then
replayed its stored result in 15.8 seconds. No mathematical discrepancy was
found.

This is a hostile review, not independent clean-room verification: the
type-`3+3` package remains `DERIVED`.

## Candidate combined theorem

If a clean-room verifier accepts both lanes, all four endpoint edge types are
covered, so principal-block monotonicity gives

```text
n3=4158 => rank_F7(M)>=28.
```

Equivalently, using the already verified universal floor 27,

```text
rank_F7(M)=27 => the graph contains an induced triangular prism.
```

This is a candidate higher-order motif consequence. It is not universal
rank 28 away from the endpoint, does not force rank 27, and does not exclude
the endpoint because ranks 28 through 44 remain arithmetically possible.

## Resource and status wall

The full even-type replay used one foreground process, took 325.41 seconds,
and left 61.73% of host physical memory free. No background worker was
started.

```text
combined endpoint rank_F7(M)>=28: CANDIDATE
universal rank_F7(M)>=28:         NOT PROVED
strict upper bound n3<4158:       NOT PROVED
graph construction:              NONE
Conway-99:                        UNKNOWN
novelty/priority:                 UNKNOWN
```

The requested verifier should independently reconstruct the signature
spaces and interaction tables, enumerate the 332/1,352 low-border streams,
replay all projected matching checks, rebuild both pivot/mate CSPs, plant
rank-two positive controls, and attack matching-degree and symmetry
conventions.
