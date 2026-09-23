# Wave 54 construction: centered ternary formal enumerator

```yaml
role: construction
date_utc: 2026-07-27T19:49:20Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: CANDIDATE
scope: ordinary integral MacWilliams feasibility at the centered ternary endpoint boundary
inputs:
  attempts/wave39-simultaneous-bh/exact-results.json: 1aab10ae2bf080d682a22d6c1e66a29f001ab2a889dc6b190b67fe0a0e0ad77d
method: exact integer Krawtchouk and MacWilliams reconstruction
outputs:
  attempts/wave54-centered-enumerator/exact-results.json: d7f8da8862c74da08e5d122e028f95125051d4e3032287f8e2e7f5490ded3cd8
limitations:
  - formal enumerator only
  - no code, point set, graph, upper-bound improvement, or novelty claim
  - independent verification required
```

## Result

The current ordinary weight-enumerator constraints are exactly feasible.  One
seven-weight formal distribution is

```text
{0:1, 18:2, 144:53316, 153:19798, 159:98496, 162:5072, 198:462}.
```

All 232 ordinary MacWilliams coefficients are nonnegative integers,
`B_1=B_2=0`, the recorded lower bounds at dual weights `7,12,13,14` hold, and
`B_i>=A_i` for all `i`.

This is a negative result for the one-variable enumerator attack.  The next
code-space experiment must retain symbol compositions or joint incidence
with the 99 distinguished weight-seven dual words.  The formal distribution
does not establish that any code or graph exists, and independent
verification is still required.
