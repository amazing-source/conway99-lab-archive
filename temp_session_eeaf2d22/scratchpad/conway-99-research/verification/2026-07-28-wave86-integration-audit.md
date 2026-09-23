# Waves 80--86 alternative-space integration audit

```yaml
role: orchestrator
date_utc: 2026-07-28T00:44:19Z
git_commit: fd88280eb25aecd8c40d9e82f572813f1c850ec5
claim_label: VERIFIED
scope: conditional coding, labelled norm-16, integral-orthogonal, and full level-seven modular-form consequences for a hypothetical srg(99,14,1,2), plus one UNKNOWN bounded SAT report
inputs:
  - path: logs/2026-07-27-wave78-public-checkpoint.json
    sha256: 3e4c5a4ec053d97c4e29fe42b377b34d8cfff4f56185ff2f04dde42104a41318
  - path: attempts/wave80-f7-overlattice-code/package-manifest.sha256
    sha256: 51d3e709308851ba9c9c63a8897dec4c761ce11e5126633e0cdf67f6e470cba7
  - path: verification/wave80-f7-overlattice-code/package-manifest.sha256
    sha256: 25129c86f97c8f9513eff04ada641c458b924f8edd583e6e6abc76d114c64077
  - path: attempts/wave81-norm16-labeled-design/package-manifest.sha256
    sha256: 6c05ff8ef0f97b1c9af0a1fbe1106ec07f826e819869660262fe92b9478033bd
  - path: verification/wave81-norm16-labeled-design/package-manifest.sha256
    sha256: 311b7a0f8fbb330bf98c9d64d3517b9602ac86c818f830bb10f2bcc09091b0af
  - path: verification/wave81-norm16-graphical-refinement/package-manifest.sha256
    sha256: 2461dbf6d3169cff5f951f519bfe57a374e00d0d3c05b51f991bb070a1ed7d63
  - path: attempts/wave82-seidel-orthogonal/package-manifest.sha256
    sha256: bc53c1a8f1425e4cbc4c2f78cee036b0e11f364d429cd9adabc55be6956dfaca
  - path: verification/wave82-seidel-orthogonal/package-manifest.sha256
    sha256: 71bf5beea4c2a5ae0ddbd3921d59d01b780c74a0985e48791196c32337943085
  - path: attempts/wave84-rooted-sat-portfolio/package-manifest.sha256
    sha256: 1373295e05624a039fd5db9a50b6744f6b57d665cdfda1e2531b60775e4bee22
  - path: attempts/wave86-level7-exact/package-manifest.sha256
    sha256: c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d
  - path: verification/wave86-level7-exact/package-manifest.sha256
    sha256: cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2
method: validate every package seal, replay independent exact checkers, preserve the Wave 86 literature correction, and publish Wave 84 only as an UNKNOWN null report
outputs:
  - verification/2026-07-28-wave86-integration-audit.md
  - verification/2026-07-28-wave86-orchestrator.md
  - logs/2026-07-28-wave86-public-checkpoint.json
limitations:
  - every promoted theorem is conditional on a hypothetical target and its stated verified imports
  - the norm-16 census contains necessary candidates, not a simultaneous outside graph
  - the modular lower bound has no verified matching upper bound
  - bounded SAT timeouts are not evidence of satisfiability or unsatisfiability
```

## Verdict

`PASS_WITH_LITERATURE_CORRECTION`.

All ten package manifests replay against their sealed files. Fresh local
testing passes 18 Wave 80 tests, 26 Wave 81 tests, 16 Wave 82 tests, and 17
Wave 86 tests. The initial combined Wave 81 pytest collection hit a duplicate
test-module basename; separate package invocations passed all tests, so this
was a harness namespace collision rather than a mathematical failure.

## Characteristic-seven code

Conditional on the verified lattice transfer, evaluation on the 99 marked
vectors is injective and gives a `[99,44]_7` code `C` with

```text
C intersect C-perp = row_F7(2A-J+I).
```

If `r=rank_F7(2A-J+I)` and `q=44-r`, then `C/R` is the non-split orthogonal
space `O^-(q,7)`. In the hardest row `r=28,q=16`, the ambient reduced space
is `O^-(42,7)` and the orthogonal complement is `O^+(26,7)`. Complete
support-five checking proves `d(C-perp)>=6`, equivalently orthogonal-array
strength five. All forced norm-14, norm-16, and norm-18 profiles remain
allowed.

## Exact norm-16 labelled boundary

The full anchored `8+8` support census contains 1,800 matrices in five
`S8 x S8` orbits. Exact deficiency coupling leaves 4,985 multisets and every
support orbit. Outside moments force the induced edge count on the eight
degree-two outside vertices to be zero or one. The base verifier retains 43
degree rows at `t=0` and seven at `t=1`; an independently checked graphicality
filter removes exactly three `t=0` rows, leaving 40 plus seven.

These are marginal and degree-level necessities. The six outside subgraphs
have not been realized simultaneously, and the norm-16 branch remains live.

## Integral-orthogonal equivalence

For `S=2A-J+I`, set

```text
T=9S+7J=18A-2J+9I.
```

The target graph is exactly equivalent to a symmetric integral matrix with
diagonal 7, off-diagonal alphabet `{-2,16}`, row sum 63, and
`T^2=3969I`. Its conditional Smith form is

```text
diag(1, 9^(r-1), 63^(99-2r), 441^(r-1), 3969).
```

Every surviving rank `r in {28,30,32,34,36,38,40,42}` passes the abstract
Smith checks. This reformulation exposes integral-orthogonal and local-global
matrix methods but does not itself remove a rank.

## Full level-seven modular constraint

In the `q=16` row, the complete space `M_22(Gamma0(7))` has dimension 15 and
Sturm bound 14. Exact Fricke transfer and nonnegative theta coefficients give

```text
N14+N16+N18 >= 1997236/341.
```

Wave 71's independently verified congruence
`N14+N16+N18=2 mod 14` rounds this to

```text
N14+N16+N18 >= 5868.
```

The verifier found a citation-level correction. The printed transformation
equation in the cited source omits a normalization ratio; combining the
source's normalization and preceding transformation equations yields the
factors actually used. Independent exact and numerical controls confirm those
factors, so the inequality is unaffected.

## SAT chronology

Wave 84 ran three CaDiCaL configurations and one Kissat configuration for
900 seconds each against the exact 1,233,001-variable, 4,323,943-clause
rooted formula. All four runs ended without a model or proof. The package is
published only with claim label `UNKNOWN`; conflict counts and timeouts are
not certificates.

## Promotion boundary

```text
evaluation-code theorem and dual distance:       VERIFIED
norm-16 support/coupling and graphical census:   VERIFIED
integral-orthogonal equivalence and Smith form:  VERIFIED
q=16 short-vector lower bound 5868:              VERIFIED
Wave 86 source normalization issue:              CORRECTED IN AUDIT
Wave 84 bounded SAT result:                       UNKNOWN
rank r=28 excluded:                              NO
strict upper bound below 4158:                   NOT PROVED
rigorous interval:                               708 <= n3 <= 4158
Conway-99 / novelty:                             UNKNOWN
```
