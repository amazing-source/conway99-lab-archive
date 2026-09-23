# Wave134 Z4 symmetrized-enumerator report

```yaml
role: construction
date_utc: 2026-07-28T08:05:12Z
git_commit: aef7b93124f8caeb1a7487f58289436bc4118880
claim_label: DERIVED
scope: >-
  Conditional Z4 code types, torsion symmetry, sparse symmetrized
  MacWilliams transform, and all graph-forced coefficient patterns on
  supports of size at most three for a hypothetical srg(99,14,1,2).
inputs:
  - path: agents/2026-07-22-wave2-algebra-codes.md
    sha256: 999cbb0366a984ab6ddf4a2ff084eb680beffaad47c0b8176752a5a6769cc0e9
  - path: verification/2026-07-22-wave2-audit.md
    sha256: b438e45544c1675530084a7a16396d2a45d4dab473a04696ddec6a9ce45641c8
  - path: attempts/wave131-binary-lcd-enumerator/package-manifest.sha256
    sha256: c305de05df2001d869db3dbfc14f7a2a8c7f305ce43471c56c66dc775e89d576
  - path: attempts/wave132-distinguished-biweight/package-manifest.sha256
    sha256: 0b99e87b0f39b1c203709d34ffba3f7b5c94f0078c53fe4020dfc3cd03ec510c
method: >-
  Replay the Smith invariants and code types, identify 2*1 as the extra
  torsion word in both codes, quotient the 5050-state transform by exact
  torsion and parity symmetries, and enumerate coordinate membership masks
  for every allowed coefficient vector through support size three.
command: >-
  python -B attempts/wave134-z4-symmetrized-enumerator/exact_check.py
  --verify attempts/wave134-z4-symmetrized-enumerator/exact-results.json
outputs:
  - path: attempts/wave134-z4-symmetrized-enumerator/package-manifest.sha256
    sha256: 581678d37091754f4bf1f197223a120d82f3051020a45b601e84889dfdad81e9
  - path: attempts/wave134-z4-symmetrized-enumerator/exact-results.json
    sha256: 8d3e39c4360341f7d3d6b8ac496853c0ae19e546ab8655cc6939b36edbddb1a2
  - path: attempts/wave134-z4-symmetrized-enumerator/search-status.json
    sha256: d5d85b9df1d2664cb808cb9eacfffb069ad6e401e73a6e4cf5e956cbcd02fddb
limitations:
  - Corrected rational and integral feasibility remain UNKNOWN_NOT_RUN.
  - No Z4 code, adjacency matrix, graph, or Conway-99 resolution is produced.
  - Novelty remains UNKNOWN.
```

The final exact forced tables contain 42 primal torsion orbits
(84 expanded compositions, 8,557,760 distinct words) and 22 dual torsion
orbits (44 expanded compositions, 4,126,784 distinct words).

Two verifier vetoes materially changed the preseal model:

1. The initial named-family table omitted mixed odd/even coefficients.
   The corrected table includes every coefficient in `{1,2,3}` on primal
   row supports through size three and every even-sum coefficient pattern
   on dual closed-neighborhood supports through size three.
2. The initial dual state quotient allowed odd-symbol weight 92.
   Since `Res(Cperp)=D intersect 1^perp`, `1` lies in `D`, and `d(D)>=8`,
   complementing a nonzero even residue word proves its weight is at most
   91, hence at most 90. Four weight-92 orbits moved to the forced-zero
   face, correcting the transform partition from `1118/157` to
   `1114/161` allowed/forbidden dual orbits.

All provisional solver runs used the earlier undercounted model and are
explicitly invalidated. They supply no feasibility or infeasibility evidence.
