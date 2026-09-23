# Wave 39 integration audit

Date: 2026-07-27 UTC

Base commit: `37f635ab67d2348c73986fae5e81b9b7a40a345a`

Verdict: **PASS for the independently verified scoped claims; the endpoint,
general upper bound, Conway-99, and novelty remain `UNKNOWN`.**

## Integrated evidence

The Wave 39 replay executed 62 tests:

| Package | Discovery | Independent |
| --- | ---: | ---: |
| Edge-local characteristic-seven rank | 8 | 14 |
| Branch-15 proof shard | 14 | 6 |
| Cross-base projection lane | 10 | 0 |
| Simultaneous `B/H` lane | 10 | 0 |
| **Total** | **42** | **20** |

Every test passed. Exact discovery and independent result files regenerated
byte-identically. All six package manifests validate. Strict JSON and YAML
parsing, status-scope tests, hostile rank/status mutations, local Markdown
links, privacy markers, and `git diff --check` were included in the integration
gate.

## Promoted results

1. For an arbitrary edge `xy` with triangle mate `z`, the 24 vertices in
   `X=N(x)-{y,z}` and `Y=N(y)-{x,z}` carry three perfect matchings. Their union
   has one of the eleven cycle types indexed by the positive partitions of
   six. A clean-room verifier exhausted all 10,395 pulled-back matchings and
   independently obtained the local characteristic-seven rank formula

   ```text
   rank = 25 - 2*(number of even parts).
   ```

   Rank transport through `N M N^T=27I-9A+J` therefore gives the universal
   necessary condition `rank_F7(M)>=19`. At the prism-free endpoint only the
   types `2+2+2`, `2+4`, `3+3`, and `6` survive, with local ranks
   `19,21,25,23`. The arithmetic rank-pair census falls from 528 to 429.

2. In refined endpoint branch 15, the existing units `x24=1` and `x2=1`
   force `x3591=0`; assuming `x187=1` then violates a frozen wedge clause.
   Exact produced raw and kernel pseudo-Boolean proofs, and fresh independent
   VeriPB 3.0.2 runs accepted both as `VERIFIED UNSATISFIABLE`. Thus branch 15
   entails `x187=0`. The other polarity shard remains open, so branch 15 is
   unresolved and complete endpoint proof coverage remains `0/33`. CakePB
   supplied no conclusion and is not claimed as an additional replay.

## Retained discovery-only restrictions

The cross-base lane derives at least twelve equal-projection pairs in each
84-triangle vertex star on the conditional `r3=12` endpoint boundary,
producing explicit support-four or support-six factor-row dependencies. It
also records rank-ten and determinant-compatible rank-eleven quotient controls
that refute a proposed universal local rank-twelve shortcut.

The simultaneous `B/H` lane derives a projective self-orthogonal
`[231,11]_3` code boundary and exact conditional edge/triangle decompositions
for a compatible `H`. Its oriented Delsarte transforms are all nonnegative.
Neither discovery-only lane is promoted to a contradiction or verified global
completion theorem.

## Status wall

No graph, complete SAT assignment, endpoint-wide UNSAT proof, completed
solve--cut--check sequence, prism-forcing theorem, or general upper-bound
improvement exists. Hence:

```text
branch-15 positive x187 shard: VERIFIED UNSAT
branch 15 / endpoint coverage: UNKNOWN / 0 of 33
rank_F7(M)>=19:                VERIFIED
upper bound below 4158:        NOT PROVED
rigorous interval:             708 <= n3 <= 4158
n3=4158 / Conway-99:           UNKNOWN
novelty and priority:          UNKNOWN
```
