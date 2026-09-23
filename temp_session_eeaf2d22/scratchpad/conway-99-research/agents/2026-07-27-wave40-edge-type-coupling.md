# Wave 40 proof B: global edge-type coupling

```yaml
role: proof_b
date_utc: 2026-07-27T03:33:27Z
git_commit: 6b28af70c67f062d687251494a047debe70a246f
claim_label: CANDIDATE
scope: "Conditional prism-free endpoint n3=4158: global edge-type surface, all-222 triangle quotients, and the exact 39-vertex Laplacian-rank bridge"
inputs:
  - "attempts/wave40-edge-type-coupling/input-freeze.sha256"
method: "Exact incidence double counting, link/face reconstruction, normalized finite quotient enumeration, Gaussian elimination over F3 and F7, and an exhaustive 18-bit lift census for one rank-11 quotient"
command:
  - ".\\.venv\\Scripts\\python.exe -B attempts\\wave40-edge-type-coupling\\exact_check.py --verify attempts\\wave40-edge-type-coupling\\exact-results.json"
  - ".\\.venv\\Scripts\\python.exe -B -m unittest discover -s attempts\\wave40-edge-type-coupling -p \"test_*.py\" -v"
outputs:
  - "attempts/wave40-edge-type-coupling/exact-results.json"
limitations: "Discovery cannot verify itself. The endpoint, all-222 case, and general upper bound remain open."
```

## Verdict

This lane does not force a prism. It exposes one exact global object and two
strict finite boundaries:

```text
global edge-type complex:                     CANDIDATE
4,050 normalized all-222 quotient census:     CANDIDATE
39-block/Laplacian rank identity:              CANDIDATE
one-quotient 2^18 pairing census:              CANDIDATE
all edges type 222 excluded:                   NO
n3=4158 and Conway-99:                         UNKNOWN
general upper bound:                           n3<=4158
```

No automorphism or transitivity of a completed graph is assumed.

## 1. The opposite-edge stars form faces

At the endpoint, the opposite-edge graph `J` on the 693 graph edges and the
`N3` relation graph `L` on the 231 graph triangles both have 4,158 edges.
There is an exact bijection

```text
E(J) <-> E(L).
```

A `J` edge is a pair of opposite edges in a graph four-cycle. Prism-freeness
makes its two side triangles an induced `N3`, hence an `L` edge. Conversely,
the two cross edges of an `N3` are opposite in its induced four-cycle.

Fix a graph edge `e=xy`. The twelve `J` edges incident with `e` map to the
simple two-regular bipartite graph `K_e` between:

```text
six nonbase graph triangles through x,
six nonbase graph triangles through y.
```

The components of `K_e` have lengths `2m`, where the positive parts `m`
give the Wave 39 edge type. Use those components as faces. Every `L` edge
lies on exactly two face boundaries, one for either cross edge in its `N3`.

If `(a,b,c,d)` count types `(222,24,33,6)`, exact face counts are

```text
F4=3a+b, F6=2c, F8=b, F12=d,
F=3a+2b+2c+d,
4F4+6F6+8F8+12F12=8316=2|E(L)|.
```

The same formulas count pairs `(base edge, induced cycle)` of lengths
`8,12,16,24` in the original graph.

## 2. Triangle links and the surface normalization

For a graph triangle `T`, the link of its vertex in the edge-type complex
has:

```text
36 vertices, degree 2.
```

It is canonically the line graph of the cross-fibre two-factor in
`G[N(T)-T]`: an `R2` partner triangle corresponds to its cross-fibre edge,
and a graph edge leaving `T` joins the two partner triangles using its
outside endpoint. Entering a fibre forces departure to the third fibre, so
every link cycle has length divisible by three. Prism-freeness excludes
length three; all lengths are at least six.

Split a triangle-vertex when its link is disconnected. The result is a
disjoint union of closed combinatorial surfaces. If

```text
H=sum_T(number of link components at T),
```

then

```text
chi=H-4158+(3a+2b+2c+d).
```

For all-`222`, there are 2,079 quadrilateral faces and

```text
-1848<=chi<=-693.
```

This is not contradictory: closed surfaces can have arbitrarily negative
Euler characteristic, and orientability has not been derived.

## 3. Three all-`222` sides around one triangle

Contract the six internal matching edges in each of the three twelve-point
fibres around `T`. The side systems become the three bipartite blocks of a
simple four-regular tripartite graph `P_T` on `6+6+6` vertices.

For three `222` sides, fix the first block. The pair partition induced by
the second block on their shared part has exactly three stabilizer orbits:
it shares three, one, or zero pairs with the fixed partition. Normalize the
second block using the third-part labels. The last block has

```text
15*15*3! = 1,350
```

possibilities in each orbit, for 4,050 complete normalized labelled forms.
Exact elimination gives:

| `rank_F3(P_T-I)` | forms |
| ---: | ---: |
| 11 | 8 |
| 12 | 1 |
| 13 | 400 |
| 14 | 46 |
| 15 | 2,616 |
| 16 | 979 |

All eight rank-11 forms have quotient components

```text
(2,2,2)+(4,4,4)
```

and exactly sixteen triangles. Therefore the joint assumptions

```text
r3=12 and every graph edge has type 222
```

force this `4+8` component boundary at every base triangle, using the
independently verified inequality `rank_F3(P_T-I)<=r3-1`.

An explicit cubic triangle-free 36-vertex lift meets the audited local
codegree caps and has the required nonnegative `B B^T` of rational rank 33.
Thus the one-triangle axioms do not exclude the boundary.

## 4. Exact 39-block rank reduction

Let `A_X` be the adjacency matrix of the 36-vertex cubic graph
`G[N(T)-T]`. For

```text
K=J-I-2A over F_7,
```

the principal 39-block on `T union N(T)` satisfies

```text
rank_F7(K[T union N(T)])=1+rank_F7(3I-A_X).           (1)
```

The base-triangle block is `I-J`, invertible over `F_7`. Its Schur
complement vanishes on the three fibre constants and equals

```text
-I-2A_X=-2(A_X-3I)
```

on their 33-dimensional orthogonal complement. Since `A_X-3I` has rank two
on the fibre constants, (1) follows. The problem is exactly a mod-seven
Laplacian/critical-group rank problem for the neighbor core.

This also catches a dangerous shortcut: `P_T` does not determine the
39-block. It omits one endpoint-pairing bit at each of its eighteen
vertices, and different lifts of the same quotient can have different
39-block ranks.

For the explicit rank-11 quotient, exhaustive enumeration of all `2^18`
pairing masks leaves 37,378 triangle-free lifts:

| 39-block rank | lifts |
| ---: | ---: |
| 33 | 264 |
| 34 | 7,348 |
| 35 | 29,766 |

The minimum 33 and its canonical witness are exact for this quotient only.
They are not a universal rank-33 theorem.

## 5. Remaining target

The smallest clean combinatorial target is to prove that the rank-11
`4+8` selections cannot be compatible across all seven triangle-stars at
every original vertex, or to exclude them with a simultaneous 60-column
`B` and compatible `H`.

The clean characteristic-seven target is to bound the mod-seven nullity of
`3I-A_X` across **every** admissible 36-vertex core. A quotient-only census
is insufficient.
