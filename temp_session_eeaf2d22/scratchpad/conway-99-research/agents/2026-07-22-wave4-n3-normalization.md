# Wave 4 theorem-forced `N3` normalization

```yaml
role: proof_b
date_utc: 2026-07-22T21:49:18Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
base_commit: d1b6d3d237bac44d10123b7d190c46f092d74eee
integration_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
claim_label: DERIVED
scope: equisatisfiable normalization of the unrestricted target existence search up to global relabeling, conditional on the cited-and-derived universal N3 consequence
inputs:
  code/root_model.py: 2a1f074f29f2e00e38437bf81418771d57ab41335605b9f3b9f2cae061a1624e
  code/sat_model.py@d1b6d3d237bac44d10123b7d190c46f092d74eee: 6e0adfbd3684f1948087e62f796b4302d6088173ee2d179213f13c3634e0b086
method: exact induced-subgraph derivation and exhaustive BFS under explicit scaffold generators
command: .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
outputs:
  code/sat_model.py@98ee7b3: c29744c4835306d576a8625b3951b51815f0a5f806a9c93c6c8eff494639276c
  code/test_sat_model.py@98ee7b3: 6c35d8bfad0110abf6808a68fe82d4af6cdbace9fe978404d079f2c979b46344
  code/test_root_model.py@98ee7b3: 5e69fc99e8270da46e8544393cf6d7c22ab1fa25268dca04cbf8e16b36472d62
limitations: legacy 11 matching representatives cannot be naively combined; their joint stabilizer needs a separate cover
```

Every putative graph contains an induced `N3`. Name its triangles

```text
{x,u,v}, {a,b,c}
```

with only the cross-edges `x-a` and `u-b`, and choose `x` as the root. Then
`u,v` are a matched root-neighbor pair. If `t` is the scaffold mate of `a`,
the residual labels are

```text
label(b) = {u,a},
label(c) = {a,h}.
```

Inducedness gives `h` outside the pairs of `u` and `a`: it is not `u` or `v`,
and `h=t` would make `t` a second common neighbor of the adjacent pair `a,c`
in addition to `b`. The scaffold group `C2 wreath S7` can therefore relabel
the three distinct coordinate pairs as

```text
u=0, v=1, a=2, t=3, h=4, mate(h)=5.
```

The two residual vertices are consequently

```text
b = label (0,2), residual index 0,
c = label (2,4), residual index 24.
```

Their edge is the only adjacency of this induced `N3` not fixed by the rooted
matching/incidence scaffold. In full graph numbering the six vertices are
`0,1,2,3,15,39`, with exact table

```text
present: x-u, x-v, x-a, u-v, u-b, a-b, a-c, b-c
absent:  x-b, x-c, u-a, u-c, v-a, v-b, v-c.
```

Thus the entire theorem-forced normalization is the positive residual unit

```text
edge_literal(label_index[(0,2)], label_index[(2,4)]) = +24.
```

The scaffold orbit of this unordered residual pair has 840 elements, exactly
all intersecting-label pairs whose two nonshared coordinates are not mates:

```text
14 * (binom(12,2)-6) = 840.
```

Its setwise stabilizer has order 768 and is isomorphic to
`C2 x (C2 wreath S4)`. Hence fixing the third coordinate pair to `(4,5)` is
safe global relabeling, not a completed-graph automorphism assumption.

For the native target encoding, the unit changes only these counts:

| item | before | after |
|---|---:|---:|
| variables | 289,338 | 289,338 |
| ordinary clauses | 285,852 | 285,853 |
| native `AtMost` constraints | 5,838 | 5,838 |
| OPB constraints | 291,690 | 291,691 |

The CLI exposes this as `--n3`. It deliberately rejects `--n3` together with
the legacy `--branch` representatives: those 11 representatives were selected
under a larger stabilizer that can move the normalized witness, so their
intersections are not a proved complete cover. The unbranched `--n3` formula
is the safe unrestricted search.
