---
role: verifier
date_utc: 2026-07-27T06:20:00Z
git_commit: 4f1754a28723a8e0e4ea3025312cd264b1b117d2
claim_label: VERIFIED
scope: >
  Secondary clean-room verification that every hypothetical
  srg(99,14,1,2) satisfies rank_F7(M)>=26.
inputs:
  verification/wave41-rank26-secondary/input-freeze.sha256: frozen
  attempts/wave41-evenpart-equality/exact-results.json: 8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85
method: >
  Freeze verified Wave 39/40 premises; independently reconstruct all eleven
  labelled local types and the exact 27+12 singular Schur reduction; exhaust
  every minimum-F permutation; cover all 10,395 third-fibre matchings by
  pivot-mate reconstruction for rank one and exact vectorized scans for
  ranks two and three; audit all four all-odd types; freeze; then compare the
  specified discovery result and primary verifier only for discrepancies.
limitations:
  - Conway-99 existence and the endpoint n3=4158 remain UNKNOWN.
  - No graph, endpoint contradiction, improved n3 bound, novelty, or priority claim is produced.
---

# Result

Verdict: **PASS**.

The secondary checker independently recovers:

```text
11 local partition types
164,928 minimum-F permutations
52 canonical right kernels
164,278 canonical equality targets
0 rank-25 matching completions
```

The four all-odd Schur cases and seven even-part cases are disjoint and
complete. Exact rank transport therefore gives

```text
rank_F7(M)>=26.  VERIFIED
```

The specified discovery SHA is exact, and the final discovery, primary, and
secondary invariants agree with no theorem discrepancy. The primary's
transient positive-control lift bug did not affect the legal matching census
or theorem.
