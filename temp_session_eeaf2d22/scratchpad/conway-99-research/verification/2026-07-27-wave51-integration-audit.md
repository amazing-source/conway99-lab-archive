# Wave 51 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T19:21:53Z
git_commit: 7a77446e8f1aa163170ff91e3b5068482603898b
claim_label: VERIFIED
scope: exact aggregate triple tensor, corrected Seidel-Smith theorem, and fixed balanced 174-cut rational relaxation
inputs:
  - path: attempts/wave51-global-triple-tensor/package-manifest.sha256
    sha256: 1edd950a677000bd931c0ac4b7f723f1b9d9460c24f6b70921c44184b79359a5
  - path: verification/wave51-global-triple-tensor/package-manifest.sha256
    sha256: 482539a3c1c5f6621d678be0247a6dbaedc8473def64dc5ad8cc6cea9e0aa8d7
  - path: attempts/wave51-seidel-smith/package-manifest.sha256
    sha256: dfb39e94b6837e21959bc2b70a9e296baacc94b4c08cb0b78e04264686685965
  - path: verification/wave51-seidel-smith/package-manifest.sha256
    sha256: bb191148dac5558d9154ea98dbb6f45da146e0602940297131ca7de211d3274c
  - path: verification/wave51-rankone-cut-relaxation/package-manifest.sha256
    sha256: b54d0ab21b72348d4de8d023f9d1cab39055c17c6f838eb3ecb1430f4d95add0
  - path: verification/wave51-rankone-cut-relaxation-independent/package-manifest.sha256
    sha256: 0372f7a810f8243e5972e8d902155ab4c3fca3256ecf71d52afeb809a61d7017
method: discovery/verifier separation, exact replay, hostile controls, source-status correction, and scope audit
outputs:
  - verification/2026-07-27-wave51-integration-audit.md
limitations:
  - all three results are necessary-condition or finite-relaxation statements
  - no full PSD, integer, graph, endpoint, strict-upper-bound, novelty, or priority claim is promoted
```

## Verdict

`PASS_SCOPED` for the corrected finite claims below. The endpoint and
Conway-99 remain `UNKNOWN`.

## Accepted exact results

### Symmetric aggregate triple tensor

The verifier independently reconstructs the exact nonnegative tensor for the
five triangle-pair relations, its five integral slices, all margin and matrix
identities, and all 125 balance equations. This verifies feasibility of the
aggregate triple relaxation.

The same verifier obtains exactly 100 failures among 625 association-algebra
associativity checks, first `81 != 153`. Therefore the displayed averages are
not intersection numbers of an association scheme. They are not a graph
construction, and actual pair-local tables may vary.

### Conditional Seidel Smith form

After correcting one discovery statement, the verifier proves

```text
SNF(S) = diag(1^r,7^(99-2r),49^(r-1),490).
```

The correct rational spectrum is `-70^1,+7^54,-7^44`. The discovery package's
reversed nonprincipal multiplicities are `REFUTED` and retained in the record.
The spectrum correction leaves the absolute determinant, Smith form,
mod-seven Jordan type, and `r>=14` symmetric-square bound unchanged. All
seventeen imported endpoint ranks 28 through 44 survive.

### Fixed balanced 174-cut relaxation

The source agent chose the cut bundle, constructed the rational witness, and
checked it. Its self-assigned verified status is therefore rejected; the
source chronology is `CANDIDATE`.

A different verifier freezes fourteen source inputs and reconstructs all 170
Wave 44 equations, 17 Wave 45 cuts, 136 Wave 47 cuts, 21 Wave 49 cuts, and
5,691 Wave 49 tensor evaluations. Exact substitution verifies the stored
support-136 rational witness with `h11/4=4158`, active coefficient rank 209,
66 tight cuts, and 108 strict cuts. This proves only that the fixed bundle is
feasible over the rationals and hence cannot yield a Farkas contradiction.

During the audit a non-evidentiary Wave 49 numerical artifact was rerun and
changed in the working tree. The mutation was quarantined recoverably, the
public sealed hash `1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152`
was restored, and the clean-room verifier replayed against those sealed
bytes. The quarantined numerical rerun is not evidence and is not published.

## Promotion boundary

```text
aggregate triple relaxation:             FEASIBLE, VERIFIED SCOPED
average association scheme:              REFUTED
conditional Seidel Smith form:           VERIFIED CORRECTED SCOPED
Seidel rank floor from this lane:         14, weaker than known 28
fixed balanced 174-cut relaxation:        FEASIBLE, VERIFIED SCOPED
fixed-bundle Farkas contradiction:        REFUTED
pair-specific quadruple compatibility:   UNKNOWN
full PSD/integer count region:            UNKNOWN
endpoint proof coverage:                  0/33
strict upper bound below 4158:            NOT PROVED
rigorous interval:                        708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:   UNKNOWN
```
