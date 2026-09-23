# Wave 40 edge-type coupling

Status: **CANDIDATE pending independent verification**. The prism-free
endpoint and Conway-99 remain **UNKNOWN**.

This package glues the Wave 39 edge-local partitions into one global
incidence object without assuming that a hypothetical graph is
vertex-transitive, edge-transitive, or has any nontrivial automorphism.

## Global edge/triangle surface

At the prism-free endpoint, let `J` be the 12-regular opposite-edge graph on
the 693 graph edges and let `L` be the 36-regular `N3` relation graph on the
231 graph triangles. Both have 4,158 edges. Mapping a `J` edge to the two
side triangles of its induced `N3` is a bijection

```text
E(J) <-> E(L).
```

For a graph edge `e=xy`, the image of the twelve-edge star `J(e)` is the
two-regular bipartite graph `K_e` between the six nonbase triangles through
`x` and the six through `y`. Its cycle partition is exactly the Wave 39 edge
type. Regard every component of every `K_e` as a face. Every `L` edge lies on
exactly two such faces, one for each cross edge of its `N3`.

If `(a,b,c,d)` count edge types `(222,24,33,6)`, then the face counts are

```text
F4  = 3a+b,
F6  = 2c,
F8  = b,
F12 = d,
F   = 3a+2b+2c+d,
4F4+6F6+8F8+12F12 = 8,316 = 2|E(L)|.
```

For a graph triangle `T`, the link of its vertex in this complex is the line
graph of the cross-fibre two-factor in `G[N(T)-T]`. Hence every link
component is a cycle whose length is divisible by three and is at least six.
Splitting a triangle-vertex when its link is disconnected gives a disjoint
union of closed combinatorial surfaces. If

```text
H=sum_T(number of link components at T),
```

their total Euler characteristic is

```text
chi = H - 4158 + F.
```

This is a genuine coupling of all edge types, all 231 graph triangles, all
4,158 opposite-edge pairs, and the local cross-fibre systems.

It does not itself contradict the all-`222` case. Then there are 2,079
quadrilateral faces, `231<=H<=1386`, and

```text
-1848 <= chi <= -693.
```

Closed surfaces can have arbitrarily negative Euler characteristic, and this
lane neither assumes nor derives orientability.

## Exact all-`222` three-side census

Around a base graph triangle `T`, contract the six matching edges in each of
its three twelve-point fibres. The three side graphs `K_e` become the three
bipartite blocks of a simple four-regular tripartite graph `P_T` on
`6+6+6` labels.

Assuming all three sides have type `222`, the checker exhausts 4,050
normalized labelled forms. It fixes one side; classifies the pair partition
on the next side into its three exact stabilizer orbits; and enumerates all
`15*15*3!` possibilities on the last side. Exact elimination over `F_3`
gives

| `rank_F3(P_T-I)` | normalized forms |
| ---: | ---: |
| 11 | 8 |
| 12 | 1 |
| 13 | 400 |
| 14 | 46 |
| 15 | 2,616 |
| 16 | 979 |

The eight rank-11 forms all have:

```text
quotient components: (2,2,2) + (4,4,4),
triangles in P_T:    16.
```

The independently verified Wave 38 bridge says

```text
rank_F3(P_T-I) <= r3-1.
```

Consequently, under the **joint** assumptions

```text
n3=4158, every edge has type 222, and r3=12,
```

every base triangle must use this rank-11 `4+8` component boundary. This is
a strong global target, not an endpoint exclusion.

## Exact 39-vertex rank identity and scope guard

Let `A_X` be the cubic graph induced on the 36 neighbors of a base triangle
outside that triangle. Exact Schur elimination in the 39 by 39 principal
block of

```text
K=J-I-2A  over F_7
```

gives the compact identity

```text
rank_F7(K[T union N(T)]) = 1 + rank_F7(3I-A_X).       (*)
```

The base-triangle block is `I-J`, which is invertible over `F_7`. Its Schur
complement vanishes on the three fibre-constant vectors. On their
33-dimensional complement it is

```text
-I-2A_X = -2(A_X-3I).
```

Since `A_X-3I` has rank two on the fibre-constant space, (*) follows.
Equivalently, the 39-block rank is one plus the mod-seven rank of the
Laplacian of the cubic neighbor core. This exposes the exact remaining
arithmetic object: the seven-primary Laplacian/critical-group nullity.

The 18-vertex quotient `P_T` does **not** determine `A_X`. At each contracted
matching edge it omits one bit saying how the two edges toward one other
fibre pair with the two edges toward the third fibre. Thus a quotient-only
rank census would be unsound.

For the explicit rank-11 quotient used by the positive control, the checker
does exhaust all `2^18` endpoint-pairing masks. Exactly 37,378 are
triangle-free, with:

| 39-block rank over `F_7` | masks |
| ---: | ---: |
| 33 | 264 |
| 34 | 7,348 |
| 35 | 29,766 |

This proves a minimum of 33 for that one quotient and emits a canonical
rank-33 witness. It does **not** prove a universal rank-33 floor across the
other 4,049 normalized quotients or across all endpoint edge-type triples.

## Positive one-triangle control

The package includes one exact 36-vertex lift of a rank-11 quotient. It is
cubic, triangle-free, has component profile `(4,4,4)+(8,8,8)`, obeys the
local cross-fibre codegree cap, and has a nonnegative required `B B^T` of
rational rank 33.

It is only a positive control for the one-triangle relaxation. It is not a
simultaneous 60-column block design, a compatible 60-vertex `H`, an endpoint
matrix, or a Conway graph.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave40-edge-type-coupling -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave40-edge-type-coupling\exact_check.py `
  --verify attempts\wave40-edge-type-coupling\exact-results.json
```
