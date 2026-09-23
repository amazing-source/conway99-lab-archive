# Wave 53 multi-root coherent lift

Status: discovery-only `DERIVED` null result. No relation type is excluded,
and the prism-free endpoint and Conway-99 remain `UNKNOWN`.

## What is stronger than Wave 52

Wave 52 retained the complete unresolved cap CSP around one root triangle.
This package simultaneously retains two such rooted systems. For roots in
relations `K,B,C,D`, their numbers of common `K`-neighbor triangles are

```text
K: 5
B: 2
C: 1
D: 0
```

The common triangle nodes are identified, candidate nodes are identified when
they represent the same unordered triangle pair, and all 72 exact-two cap
nodes are retained. No `B/C` completion is selected before refinement, and no
automorphism of a completed graph is assumed.

For `B`-related roots, the two root cross edges use distinct endpoints. Their
two common `K`-neighbor triangles give one candidate variable shared by both
rooted cap systems. That variable is forced to `B`: the two root edges already
give two cross edges, while a third would be a forbidden triangular prism.

## Exact results

The expanded CSP has triangle nodes, unresolved candidate-`B` nodes, and
exact-two cap-incidence nodes. Exact 2-WL gives:

| root relation | triangle core | candidates | shared | CSP order | stable 2-WL colors |
|---|---:|---:|---:|---:|---:|
| `K` | 31 | 216 | 0 | 319 | 285 |
| `B` | 36 | 215 | 1 forced true | 323 | 584 |
| `C` | 37 | 216 | 0 | 325 | 321 |
| `D` | 38 | 216 | 0 | 326 | 63 |

Every stable intersection parameter is a nonnegative integer. This does not
certify graph realizability: each object is already a realized finite
incidence template, so integral WL parameters are expected.

Exact folklore 3-WL on the smaller two-root triangle cores stabilizes at:

```text
K: 107 colors
B: 321 colors
C: 240 colors
D:  61 colors
```

This extra tuple lift also gives no contradiction.

## Positive local controls

After the forced closures are fixed, a deterministic pair of bipartite
2-factor assignments is constructed for each root relation. All 72 caps have
value exactly two. The controls select 72 unique variables for `K,C,D`; the
`B` control selects 71 unique variables because its one forced-true variable
is shared by both roots.

The controls are never supplied to WL. They prove only that this merged local
cap system is feasible, not that it extends to 231 graph triangles or to an
`srg(99,14,1,2)`.

## Reproduce

The component build avoids a long silent process and gives a hash after each
root relation:

```powershell
$recordDir = "attempts\wave53-multi-root-wl\records"
New-Item -ItemType Directory -Force -Path $recordDir | Out-Null
foreach ($relation in "K","B","C","D") {
  python -B attempts\wave53-multi-root-wl\multi_root_wl.py `
    --relation $relation --output "$recordDir\$relation.json"
}
python -B attempts\wave53-multi-root-wl\multi_root_wl.py `
  --assemble-from $recordDir `
  --output attempts\wave53-multi-root-wl\exact-result.json
```

Replay the canonical envelope and each exact component:

```powershell
python -B attempts\wave53-multi-root-wl\multi_root_wl.py `
  --verify attempts\wave53-multi-root-wl\exact-result.json --envelope-only
foreach ($relation in "K","B","C","D") {
  python -B attempts\wave53-multi-root-wl\multi_root_wl.py `
    --relation $relation `
    --verify attempts\wave53-multi-root-wl\exact-result.json
}
python -B -m unittest discover `
  -s attempts\wave53-multi-root-wl -p "test_*.py" -v
```

The exact artifact is 14,032,340 bytes with SHA-256
`d99d89ef56cbd1f603cc8668b340bd7ad20993570899eaf556ee4c9a7f400717`.
The implementation uses standard-library integer arithmetic and enforces a
20% free-physical-memory floor.

## Boundary

- Discovery work cannot promote itself to `VERIFIED`.
- 2-WL sees cap incidence; the numerical right side two is checked separately.
- 3-WL is run on the triangle core, not the 319-to-326-node cap CSP.
- A positive local cap control is not a graph construction.
- No global transitivity, association scheme, or automorphism is assumed.
- No endpoint exclusion, improved `n3` upper bound, or Conway-99 resolution
  follows.
