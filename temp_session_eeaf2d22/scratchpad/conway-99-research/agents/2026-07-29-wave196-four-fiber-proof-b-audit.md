# Wave 196 proof-B audit: four-fiber rigidity

```yaml
role: proof_b
date_utc: 2026-07-29T05:07:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Independent hostile audit of the fixed-center four-fiber theorem,
  the inclusion of selected, old-raw, and genuinely-new exact-three
  companion pairs, the global bounds F<=1287 and J<=3564, and the exact
  conditional certificate Q>=7029.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave174-no-weight3-dual/package-manifest.sha256: ac34c8a3b045bec70e3a2080cb4365c0ea43cc732b313ecb3cec355a28f23450
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
method: >-
  SRG intersection numbers, local matching fibers, the two fixed
  Hilton--Milner equality templates at (7,3), companion-orbit separation,
  and exact rational coefficient expansion. No graph, code, cover, SAT,
  LP, configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave196-four-fiber-proof-b-audit/exact_check.py
  --verify attempts/wave196-four-fiber-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave196-four-fiber-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave196-four-fiber-proof-b-audit.md
  - attempts/wave196-four-fiber-proof-b-audit/
limitations:
  - This is a proof-B derivation and audit, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The Hilton--Milner equality classification is used as a cited theorem.
  - No endpoint graph, code, cover, or flag system is constructed.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

All four hostile-audit targets survive.  Conditionally,

```text
c_x<=13,
j_x<=36,
F<=1287,
J<=3564,
Q>=7029.
```

## 1. Four-vertex fibers

Fix `x`.  The graph on `N(x)` is seven disjoint edges, because each
neighbor has exactly `lambda=1` neighbor inside `N(x)`.  A nonneighbor
`y` of `x` has two common neighbors with `x`; they lie in distinct local
edges, since adjacent common neighbors would give their edge both `x`
and `y` as common neighbors.

Conversely, choose one endpoint from each of two distinct local edges.
The endpoints are nonadjacent, so `mu=2` gives exactly one common
neighbor besides `x`.  It is a nonneighbor of `x`: otherwise it would
have two neighbors in the matching induced by `N(x)`.  Distinct endpoint
pairs give distinct vertices because a nonneighbor has exactly two
common neighbors with `x`.

Thus each pair of local edges has exactly four vertices in its fiber,
and the `21*4=84` fibers partition the nonneighbors of `x`.

## 2. One flag uses the three pair-fibers

For a canonical flag `(x,T)` with

```text
A_x(T)={S_i,S_j,S_k},
```

the six incidences from `N(x)` to the three vertices of `T` are distinct.
Each selected local edge pairs two different leaf types.  The resulting
three-edge multigraph on the three leaf types is loopless and has degree
two at every vertex.  It is therefore the triangle, so the three leaves
have fiber types

```text
ij, ik, jk.
```

Equal `A`-sets give a forbidden weight-two relation, while disjoint
`A`-sets plus the unused seventh block and the full-star relation give a
forbidden weight-three relation.  Hence the local `A`-family is simple
and intersecting.

## 3. Nontrivial and common-star families

For an intersecting family with empty total intersection,
Hilton--Milner gives `c_x<=13`.  If `c_x<=12`, then `j_x<=36`.

At equality `c_x=13`, the `(7,3)` equality classification has the two
usual templates:

- `H`: one exceptional triple `X`, together with the triples containing
  a point `s` and meeting `X`;
- `K`: the triples containing at least two points of a fixed triple `X`.

In `H`, the three pairs `{s,t}` for `t in X` have degree five.  In `K`,
the three pairs inside `X` have degree five.  Each pair-fiber contains
only four vertices, so each of the three distinct fibers forces a repeat.
The fibers are disjoint, making the losses additive:

```text
j_x<=3*13-3=36.
```

If instead every `A` contains `S_0={x,p,q}`, each flag has one
`p`-neighbor `y` and a distinct `q`-neighbor `z` in its leaf triangle.
The nonedge `yq` has common neighbors `p,z`; `mu=2` therefore determines
`z` from `y`.  The edge `yz` then has a unique common neighbor by
`lambda=1`, determining the third leaf.  Only the 12 neighbors of `p`
outside `{x,q}` can serve as `y`.  Thus `c_x<=12` and again `j_x<=36`.

This proves the universal local theorem.

## 4. Full flag pool

The selected exact-three circuits, the `h` old exact-three companion
orbits, and the `g` genuinely-new closed residual companion orbits are
pairwise disjoint by the verified Wave194 collision audit and orbit
closure.  Wave180 canonically identifies every such orbit with one flag.
Therefore

```text
F=n3+h+g=sum_x c_x<=99*13=1287.
```

The same local theorem gives `J=sum_x j_x<=99*36=3564`.

For the selected type-three label union `U`,

```text
|U|>=C-n1-2n2.
```

Every label in `U` supplies one oriented flag label.  The `a3+b3` old-raw
assignments supply distinct oriented private labels outside `U`; the two
type-two assignments on one private nonedge have opposite centers.
Consequently

```text
J>=C-n1-2n2+a3+b3,
S36=3564-C+n1+2n2-a3-b3>=0.
```

## 5. Exact certificate

Retain the verified Wave194 rows

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C.
```

With the four raw identities and

```text
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W,
```

exact expansion gives

```text
Q0-(11C-3564)/6
 =2SI/3+4S2/3+SE2/6+2RA/3+SL/3+S36/6
  +a1/6+b3/2+c2/6+W/3.
```

Every term is nonnegative and the verified pools give `Q>=Q0`.  For
`C=4158`, the target is `7029`.  The arithmetic null row recorded in the
replay is not asserted to be an object.

## Boundary

```text
four-fiber bijection:                 DERIVED
flag pair-fiber rule:                 DERIVED
Hilton--Milner equality templates:    CITED
common-star injection:                DERIVED
g-pool inclusion:                     AUDIT PASS
F<=1287 and J<=3564:                  DERIVED
conditional Q>=7029:                  DERIVED
independent verifier promotion:       pending
endpoint contradiction:              no
Conway-99 / external novelty:         UNKNOWN
```
