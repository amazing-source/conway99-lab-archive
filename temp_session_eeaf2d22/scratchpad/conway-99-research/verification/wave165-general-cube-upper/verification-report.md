# Wave 165 clean-room mathematical audit

## Verdict

```text
VERIFIED_WITH_SCOPE:
12*C8 <= 37422 + 3*P = 41580-n3
```

The scope is every hypothetical simple strongly regular graph with
parameters `(99,14,1,2)`, using the separately verified identity
`n3+3P=4158`.

## Fixed-square partition

The target has

```text
99*(99-1-14)/2 = 4158
```

nonedges. The two common neighbors of a nonedge cannot be adjacent, since
that would give an adjacent pair two common neighbors against `lambda=1`.
Every nonedge is therefore a diagonal of a unique induced four-cycle.
Each four-cycle has two diagonals, so there are exactly 2,079 induced
four-cycles.

Fix one as `v0 v1 v2 v3 v0`. Let `a_i` be the unique outside common
neighbor of edge `v_i v_(i+1)`, and let `U_i` contain the outside vertices
adjacent only to `v_i` among the four anchors. Opposite anchors already have
their two cycle common neighbors, so no outside vertex meets an opposite
pair. The four edge apexes are distinct. Each anchor has two cycle
neighbors, two edge apexes, and ten singleton neighbors:

```text
|U_i|=10.
```

## Exact boundary matching

For `x in U_i`, the nonedge `x,v_(i+1)` has common neighbor `v_i`.
Its unique second common neighbor lies either in `U_(i+1)` or at
`a_(i+1)`. The apex `a_i` is excluded because the edge `v_i a_i` already
has `v_(i+1)` as its unique common neighbor. Thus

```text
|E(U_i,U_(i+1))| + |E(U_i,{a_(i+1)})| = 10.
```

For the nonedge `v_i,a_(i+1)`, the second common neighbor after
`v_(i+1)` lies either in `U_i` or at `a_(i-1)`. All other anchor and apex
candidates violate the already saturated `lambda=1` or `mu=2` equations.
Consequently,

```text
|E(U_i,U_(i+1))| =
  10  if a_(i-1) is adjacent to a_(i+1),
   9  otherwise.
```

The degree cap holds on both sides, so these bipartite graphs are partial
matchings.

## Marked-square/prism bijection

An adjacent opposite apex pair, for example `a_0~a_2`, combines with the
fixed square to induce a triangular prism. The apex support relative to the
square excludes every extra cross-edge.

Conversely, an induced triangular prism has exactly two base triangles and
three matching edges. Deleting the endpoints of any one matching edge
leaves one of its three rectangular induced four-cycles; the deleted
vertices are the adjacent unique apexes on opposite edges of that square.
These constructions are inverse. If `tau(F)` counts the zero, one, or two
adjacent opposite-apex pairs at a square `F`, then

```text
sum_F tau(F) = 3*P.
```

Let `D` count squares with `tau(F)=2`. Then

```text
2*D <= 3*P.
```

If `P` is odd, parity sharpens this to `2*D<=3*P-1`.

## Cube extensions

An induced cube extending `F` has opposite-face vertices
`b_i in U_i`. Its four opposite-face edges run through all four consecutive
boundary matchings. Once one `b_i` is chosen, the partial matchings
determine every successor uniquely when it exists. Therefore

```text
e_cube(F) <= 9 + indicator[tau(F)=2].
```

Extra chords can only reject a tuple; they cannot increase this upper
bound.

Every cube contains exactly six induced four-cycles. Double counting
cube--face incidences gives

```text
6*C8 = sum_F e_cube(F)
     <= 9*2079 + D.
```

Multiplying by two and using `2D<=3P`,

```text
12*C8 <= 37422 + 2D
       <= 37422 + 3P
       = 41580 - n3.
```

At `P=0`, the integer specialization is

```text
C8 <= floor(37422/12) = 3118.
```

When `P` is odd, the right side sharpens by one to `41579-n3`.

## Evidence boundary

No discovery code or solver output was used. The audit found no hidden
symmetry assumption, inducedness gap, or labelled/unlabelled multiplicity
error. The theorem controls the cube motif count but supplies no lower
bound on `W8-3*C8`; Conway-99 and literature novelty remain `UNKNOWN`.
