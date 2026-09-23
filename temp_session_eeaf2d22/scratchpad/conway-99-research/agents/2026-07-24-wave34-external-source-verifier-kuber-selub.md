# Wave 34 external-source verifier: Kuber and Selub

```yaml
role: verifier
date_utc: 2026-07-24T21:55:00Z
git_commit: 1be9b6f61136763ce77d3927984979205e7fb23a
claim_label: VERIFIED
scope: Kuber pinned conditional Lean theorem and Selub 2023 SAT framework only
method: clean external build, axiom/interface audit, and institutional-PDF scope audit
limitations: no graph-to-matrix bridge, no Selub solver result, and no Conway-99 conclusion
```

## Handoff

Kuber's project at
`be7b0ae3394721a4c3a1375008a1dbfca44981fc` passes a clean detached
Lean 4.27.0 `lake --wfail build`. All seven printed theorem axiom sets are
exactly `[propext, Classical.choice, Quot.sound]`, and the audited
`Conway99C3Orbits/Basic.lean` file contains no placeholder or unsafe escape
hatch.

The theorem is narrower than a graph theorem. It assumes an arbitrary matrix,
orbit set, diagonal classification, spectral trace certificate, and triangle
congruence. The repository does not derive those objects from a
`srg(99,14,1,2)` or an order-three graph action. Two extra packaged fields,
`quotientIdentity` and `regularity`, are unused by the endpoint.

Selub's seven-page 2023 University of Chicago REU paper is verified as older
SAT-framework prior art. It reports no completed solver run or certificate.
Its printed quadrilateral existence clause has no visible target-pair
restriction, so equisatisfiability is **not verified as printed**; its rooted
section also switches inconsistently from `v1` to `v0`.

The complete report is
[`verification/wave34-external-source-audit/kuber-selub/audit.md`](../verification/wave34-external-source-audit/kuber-selub/audit.md).
Conway-99, `n3=708`, every unrestricted Wave 34 branch, and novelty remain
`UNKNOWN`.
