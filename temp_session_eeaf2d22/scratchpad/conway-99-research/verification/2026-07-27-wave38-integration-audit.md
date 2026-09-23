# Wave 38 integration audit

Date: 2026-07-27 UTC

Base commit: `3014f3b1c010cdde1687b8878d4ec58d2bb90f03`

Verdict: **PASS for the published scoped claims; target status remains
`UNKNOWN`.**

## Integrated evidence

The integration replay executed 81 tests:

| Package | Discovery | Independent |
| --- | ---: | ---: |
| Solver harvest | 4 | 12 |
| Complete endpoint | 12 | 15 |
| Coclique rank | 8 | 10 |
| Higher order | 9 | 11 |
| **Total** | **33** | **48** |

Every test passed. The replay additionally checked the exact-result files,
strict JSON and YAML parsing, duplicate identifiers in the two ledgers,
evidence-path resolution, package manifests, Markdown local links, privacy
markers, and `git diff --check`.

## Promoted scoped results

1. The endpoint work queue contains 33 exact refined cases with normalized
   orbit weight 6644 and 231 collision-free planned artifact paths. The two
   sampled live workers produced no output and contribute proof coverage
   `0/33`.
2. The complete all-prism construction has 96,215 potential triangles and
   24,388,892,640 residual-only labelled clauses. The decoded-candidate
   oracle, candidate-bound catalog, source-bound pool, and guarded exporter
   pass independent reconstruction. Findings `W38-CE-V1` through
   `W38-CE-V5` are fixed.
3. Every hypothetical target graph contains a 13-coclique, giving the
   universal necessary condition `rank_F7(M)>=13`. At the endpoint,
   `r3=12` therefore forces even `r7>=14`; the arithmetic survivor census is
   reduced to 528 pairs.
4. Conditional on the endpoint identities, the signed simple-four-cycle
   imbalance is 200,277 and the fixed-base ternary rank bridge is exact. The
   frozen local control has rank ten and shows that the audited one-triangle
   relaxation alone cannot exclude `r3=12`.

The higher-order audit has one wording qualifier: the centered seven-row Gram
`D=C+J` has rank six, while the uncentered seven-row Gram has rank seven.

## Status wall

No target formula was solved. No candidate graph, SAT assignment, UNSAT proof,
completed lazy-cut sequence, or checked endpoint certificate exists. Hence:

```text
proof coverage:             0 / 33
upper bound below 4158:     NOT PROVED
rigorous interval:          708 <= n3 <= 4158
n3=4158:                    UNKNOWN
Conway-99:                  UNKNOWN
novelty and priority:       UNKNOWN
```
