# Independent N3-normalization audit

Verdict: `PASS` for the conditional target-only normalization. Conway-99
remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-22T22:24:40Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
claim_label: VERIFIED
scope: conditional target-only N3 normalization in the rooted srg(99,14,1,2) encoding
inputs:
  agents/2026-07-22-wave4-n3-normalization.md: b3c8111825c71378286efc76d585a4fa1c296c7c446baffabfcd457b8abee9d3
  code/sat_model.py: c29744c4835306d576a8625b3951b51815f0a5f806a9c93c6c8eff494639276c
  code/test_sat_model.py: 6c35d8bfad0110abf6808a68fe82d4af6cdbace9fe978404d079f2c979b46344
  code/test_root_model.py: 5e69fc99e8270da46e8544393cf6d7c22ab1fa25268dca04cbf8e16b36472d62
method: independent source audit, full scaffold-group enumeration, orbit-stabilizer check, focused state checks, and test replay
command: |
  cd code
  $env:PYTHONDONTWRITEBYTECODE='1'
  & '..\.venv\Scripts\python.exe' -m unittest test_root_model.py test_sat_model.py -v
outputs:
  persistent_output: not_applicable_stdout_only
  test_result: 27 tests passed
  normalized_formula_sha256: ad7a8bf5d76c3f740f3f65fee5b134cf6b8e6720e22fd780916121edd59fd0de
limitations: does not verify Makhnev's theorem, the project derivation forcing N3 occurrence, solver completeness, or target existence/nonexistence
```

## Exact normalized witness

Choose the root inside an existing `N3` and globally relabel its vertices as

```text
(x,u,v,a,b,c) = (0,1,2,3,15,39).
```

The two residual labels are `b=(0,2)` and `c=(2,4)`. The rooted scaffold fixes

```text
present: xu, xv, xa, uv, ub, ab, ac
absent:  xb, xc, ua, uc, va, vb, vc.
```

The sole undecided edge of the induced `N3` is `bc`. Its residual indices are
zero and 24, and the deterministic edge-variable ordering makes it exactly
literal `+24`. The implementation adds the single clause `[24]`, with no new
variables and no new cardinality constraints.

## Independent symmetry check

The verifier independently enumerated the full rooted scaffold group
`C2 wreath S7`. It obtained group order 645,120, orbit size 840 for the
canonical unordered residual pair, and stabilizer size 768. The stabilizer is
`C2 x (C2 wreath S4)`, agreeing with

```text
645120 / 768 = 840.
```

The orbit is exactly the intersecting-label pairs whose two nonshared
coordinates are not mates. Choosing this representative therefore uses global
vertex relabeling and the fixed-scaffold action, not an automorphism assumption
on the completed graph.

## Guard checks

Both the API and CLI reject every `pair_count` other than seven. A duplicate
normalization is rejected. The legacy matching representatives are rejected
whether added before or after the N3 unit: fixing the N3 changes the stabilizer,
so the old 11 representatives are not a proved complete joint cover.

The `VERIFIED` label applies only to this conditional relabeling and its
implementation. Universal N3 occurrence and two-vertex percolation retain the
label `DERIVED`; neither direction of the target existence question is proved.
