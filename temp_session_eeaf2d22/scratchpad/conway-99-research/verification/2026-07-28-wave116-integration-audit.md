# Waves 96 and 107--116 C4 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-28T04:29:10Z
git_commit: f07565e59de8b9b5b53280896e85fde3387e4f3e
claim_label: VERIFIED
scope: fixed-C4 short-shell incidence, conditional motif spectrum/projector/search, norm-20 graph dictionary, and corrected aggregate Jacobi-theta reduction
inputs:
  - path: attempts/wave96-norm16-norm18-upper/package-manifest.sha256
    sha256: 1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73
  - path: verification/wave96-norm16-norm18-upper/package-manifest.sha256
    sha256: 8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9
  - path: attempts/wave107-c4boxk3-spectrum/package-manifest.sha256
    sha256: 7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0
  - path: verification/wave107-c4boxk3-spectrum/package-manifest.sha256
    sha256: 48398887ca2f4dbc5283cae851ffef396ea3b4308c16105f894ac6aa5cad4e1d
  - path: attempts/wave109-c4boxk3-local-projector/package-manifest.sha256
    sha256: 6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e
  - path: verification/wave109-c4boxk3-local-projector/package-manifest.sha256
    sha256: fcbb970eebf0b92cb012f5f2e81ccb8c6315c002c1f228f830cd1b0b082e62cd
  - path: attempts/wave110-c4boxk3-symmetry-sat/package-manifest.sha256
    sha256: 1cef4ea7a81e844f10a56ccb1b5a5e0c4c7414b4efc766c486cdc666de8940ea
  - path: verification/wave110-c4boxk3-symmetry-sat/package-manifest.sha256
    sha256: 57ab8e26f872617ef9faecc7ca303c750ee1051b6455984620b27209f90e0a44
  - path: attempts/wave112-c4-short-vector-incidence/package-manifest.sha256
    sha256: f343b7d7b0bfb1ca8c7226946bcbe8b1d8c6169249911fea8493611187081c28
  - path: verification/wave112-c4-short-vector-incidence/package-manifest.sha256
    sha256: 56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024
  - path: attempts/wave116-c4-jacobi-theta/package-manifest.sha256
    sha256: 9c474c8fc6c04e382b7fd506997c7ec81cb5ea5fa38453e6f284271eda933d98
  - path: verification/wave116-c4-jacobi-theta/package-manifest.sha256
    sha256: e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8
  - path: attempts/wave118-strategy-estimate/package-manifest.sha256
    sha256: f6108a370e56bfbb07aaeffcc6edd50988c90032bb148816579dbd33418d03d4
method: replay 114 sealed manifest entries and 110 exact tests, compare separated derivations, preserve all verifier corrections, and keep every unproved cap and bounded timeout UNKNOWN
outputs:
  - verification/2026-07-28-wave116-integration-audit.md
  - verification/2026-07-28-wave116-orchestrator.md
  - logs/2026-07-28-wave116-public-checkpoint.json
limitations:
  - every graph and lattice statement is conditional on a hypothetical target
  - neither the cap-25 nor cap-24 local extension bound is proved
  - the valid Jacobi index is large and no positive upper certificate is known
  - bounded motif searches produced neither a graph nor an UNSAT certificate
```

## Verdict

`PASS_WITH_CLARIFICATIONS_AND_EVIDENCE_BOUNDARY`.

All thirteen manifests replay against 114 sealed files. Fresh testing passes
49 discovery tests and 61 verifier tests. The audit retains three essential
boundaries:

- the norm-20 theorem is verified, but the cap of 24 is not;
- the shared-potential symmetry proof is verified, but every complete
  encoding run remains `UNKNOWN_TIMEOUT`; and
- the common Jacobi reduction is verified only after replacing the invalid
  small index by the lattice-compatible `K/L` pair.

## Fixed-cycle shell squeeze

Every hypothetical target has exactly 2,079 induced four-cycles. The live
short-vector support lanes contain at least

```text
norm 14:       21 alternating C4s
norm 16:       20 alternating C4s
norm 18 h=0:   18 alternating C4s
norm 18 h=1:   26 alternating C4s.
```

At rank 28, `N14+N16+N18>=5868`, so at least one cycle has 52 oriented
extensions, equivalently 26 antipodal support pairs. A universal cap of 25
pairs would exclude the row. The sharper weighted version gives

```text
407*N16+43*N18 >= 2165002,
cap 25 => 407*N16+43*N18 <= 2115382.
```

The cap is not a consequence of dimension and minimum distance: after fixing
the alternating cycle coordinates, the norm-16 residual sphere is
40-dimensional and contains an exact 80-point cross-polytope relaxation.

## Norm-20 dictionary

Independent verification confirms that every integer norm-20
`-4` eigenvector has exactly ten `+1` and ten `-1` coordinates. Its support
has at most three same-sign edges and at least 15 alternating four-cycles.
In the rank-30 scalar row, a universal cap of 24 antipodal extensions through
norm 20 would exclude the row. That cap is a sufficient future target, not a
proved theorem.

## Conditional motif lane

Conditional on an induced `C4 box K3`, the outside graph has exact
characteristic polynomial

```text
(x-3)^42 (x+4)^32 (x^2-9x-46)
(x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2.
```

It is connected and has 549 edges, 167 triangles, and 1,356 four-cycles.
The forced incidence kernel is a primitive rank-74 lattice of determinant
`2^22*3^10*5^2`; modulo seven it is `O^-(74,7)`. The local projector admits
all imported ranks.

The complete SAT encoding with verified shared-potential symmetry has
325,852 variables and 978,711 CNF clauses. All four invariant branches
again time out without a model or proof.

## Corrected Jacobi boundary

For one induced cycle, the restricted `-4` projector has spectrum

```text
13/63, 5/7, 3/7, 3/7
```

and determinant `65/2401`. The naive marking `u_i/sqrt(7)` lies outside
`K*`, so the small index `E/2` is invalid. The lattice-compatible markings
give

```text
G_L=63E,
G_K=441E=7G_L,
det(G_K)=1023942465.
```

The aggregate coefficient at Fourier pattern
`21(1,-1,1,-1)` counts antipodal C4 incidences. Rank 28 forces at least
52,812; a cap-25 bound would be 51,975, leaving a gap of 837. No basis,
Sturm bound, positive coefficient cone, or dual upper certificate has been
produced.

## Promotion boundary

```text
C4 incidence and local partitions:       VERIFIED
weighted cap-25 implication:             VERIFIED
pointwise cap 25:                        NOT PROVED
norm-20 10+10 theorem:                   VERIFIED WITH CLARIFICATION
pointwise cap 24 through norm 20:        NOT PROVED
conditional outside spectrum/lattice:    VERIFIED SCOPED
shared-potential symmetry theorem:       VERIFIED
complete motif search:                   UNKNOWN_TIMEOUT
corrected Jacobi K/L reduction:          VERIFIED WITH CLARIFICATIONS
Jacobi upper certificate:                NOT PROVED
rank 28 or rank 30 excluded:             NO
strict upper bound below n3=4158:        NOT PROVED
rigorous interval:                       708 <= n3 <= 4158
Conway-99 / novelty:                     UNKNOWN
```
