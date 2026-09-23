# Wave 34 external-source verifier

```yaml
role: verifier
date_utc: 2026-07-24T23:40:00Z
git_commit: 37e8635298e1ce0f23726dd7f80526698c82be91
claim_label: VERIFIED
scope: Consolidation of three independently audited external-source lanes
inputs:
  status_designs_manifest: 1af4bad56405fb24128285fa586e2d1e2b80c82f1bdffdafa7cbdb6053cd6812
  harrison_manifest: 6052d3114a89af378cf412cc3126b60bab9dc9fe249a673188d3369a681db386
  kuber_selub_manifest: 5053217d6432365b903b787cb53e923996e96feef404904caad89dd7ebd686bc
method: Verify component manifests and integrate only their scoped conclusions
command: See verification/wave34-external-source-audit/run-report.yaml
outputs:
  audit:
    path: verification/wave34-external-source-audit/audit.md
    sha256: f4432e58224a484cc56230b82dd84b07b53edcf19d34e775e45e41c20d9dc4c1
  results:
    path: verification/wave34-external-source-audit/results.json
    sha256: 86d1c1ba7cead388a54a7e031086e95b71e3169999110c02e2d9645d1132271c
limitations: No external graph-level theorem is imported; Conway-99 remains UNKNOWN
```

## Handoff

The three external-source lanes pass only at their explicit boundaries.

- Current direct sources support the maintained `?` status marker, McKay's
  approximate design-scale statement, and the restricted provenance of the
  Rijeka derived corpus. None proves openness, completeness, or novelty.
- Kuber's pinned Lean project builds cleanly and verifies a conditional
  matrix/arithmetic theorem with standard Lean axioms. It does not formalize
  the graph-to-matrix bridge.
- Harrison's arbitrary-root model, builder separation, orbit coverage,
  forcing layer, exact Gram base, and 1,302 CNF recipe identities replay.
  Missing or unpulled proof bodies leave every theorem-ladder UNSAT claim
  `UNKNOWN`.
- Selub is valid historical SAT-framework prior art but reports no solver
  result or certificate. The printed quadrilateral equivalence is
  `NOT VERIFIED AS PRINTED`.

No external graph-level result is imported. Conway-99, `n3=708`, novelty, and
priority remain `UNKNOWN`.

The full consolidation is
[`verification/wave34-external-source-audit/audit.md`](../verification/wave34-external-source-audit/audit.md).
