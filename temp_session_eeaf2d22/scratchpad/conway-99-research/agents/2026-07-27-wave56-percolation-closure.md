# Wave56 proof-B: bootstrap-percolation closure space

```yaml
role: proof_b
date_utc: 2026-07-27
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: DERIVED
scope: conditional prism-free srg(99,14,1,2) nonedge closure and exact early-wave CSP
inputs:
  attempts/wave56-percolation-closure/input-freeze.sha256: frozen local inputs
  attempts/wave56-percolation-closure/source-metadata.json: primary literature metadata
method: exact closure-parameter arithmetic, all-64 labeled tip enumeration, complete six-subset prism detection, exact pair-deficit multicover
limitations:
  - discovery cannot verify itself
  - local profiles are not graph completions
  - no endpoint exclusion, strict upper bound, graph, or novelty claim
```

## Result

The closure classification and exact eigenvalue multiplicities leave only
the unique proper nonedge closure `K3 square K3`.  This gives the exact global
relations

```text
n3+3P=4158,
R=18H,
H<=231,
6H<=P,
R<=3P=4158-n3,
S>=n3.
```

The tempting equality `R=3P` is conditional: it holds exactly if every prism
extends to a rook-graph closure.  That extension is not proved.

The same closure census gives `2<=m(G,2)<=3`, and `m(G,2)=3` exactly when
`H=231`.  Thus the target-specific content of the cited Theorem 4.19 is
recovered without importing its arithmetic.

At the prism-free endpoint `P=0`, so `H=R=0`; all 4,158 nonedges percolate.
For an arbitrary nonedge, the forced `C4` and its four edge-triangle mates
have only four locally admissible labeled tip relations, and prism-freeness
leaves the empty relation.

The exact next-wave problem reduces to 23 neighborhood masks and 35 labeled
profiles, with 11 formal dihedral label-orbits.  The profile sizes are

```text
8:1, 10:8, 11:1, 12:16, 14:8, 16:1.
```

They satisfy `x2+3x3+6x4=16`.  This is a reproducible smaller CSP, but it has
local solutions and yields no global counting contradiction.
