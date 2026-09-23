# Derivation of `12*C8 <= 41580-n3`

Claim label: `DERIVED`.

Throughout, let `G` be an `srg(99,14,1,2)`. Thus `G` has 99 vertices, every
vertex has degree 14, adjacent vertices have exactly one common neighbor,
and nonadjacent vertices have exactly two common neighbors.

## 1. The global number of induced four-cycles

The number of edges is

```text
99*14/2 = 693,
```

so the number of nonedges is

```text
C(99,2) - 693 = 4851 - 693 = 4158.
```

For a nonedge `uv`, let its two common neighbors be `p,q`. The vertices
`p,q` cannot be adjacent: otherwise the adjacent pair `pq` would have both
`u` and `v` as common neighbors, contradicting `lambda=1`. Consequently
`u,p,v,q` induce a four-cycle whose diagonal is `uv`. The two common
neighbors are fixed by `mu=2`, so this cycle is unique.

Every induced four-cycle has exactly two diagonal nonedges. Double counting
nonedge--four-cycle incidences gives

```text
C4(G) = 4158/2 = 2079.                         (1)
```

This also agrees with the independently verified Wave 112 count.

## 2. The outside partition of a fixed four-cycle

Fix an induced cycle

```text
C = a0 a1 a2 a3 a0,
```

with indices read modulo four.

Each adjacent pair `a_i,a_(i+1)` has one common neighbor outside `C`,
because its two neighbors inside `C` are distinct, not common. Call this
outside vertex the edge apex `t_i`. The four edge apexes are distinct. If
one vertex served two cycle edges, it would either be adjacent to three
anchors or to an opposite anchor pair; in either case an opposite
nonadjacent pair of anchors would acquire a third common neighbor beyond
the two anchors already on the cycle, contradicting `mu=2`.

No outside vertex can be adjacent to an opposite anchor pair
`a_i,a_(i+2)`: those nonadjacent anchors already have exactly the two other
cycle anchors as common neighbors.

Now inspect the degree of `a_i`. It has:

- two neighbors on `C`;
- the two distinct edge apexes `t_(i-1),t_i`;
- ten remaining neighbors outside `C`.

None of the remaining ten can meet another cycle anchor. Meeting an
opposite anchor is impossible by the previous paragraph; meeting an
adjacent anchor would make it that edge's unique apex. Define

```text
S_i = {x outside C : N_C(x) = {a_i}}.
```

Then

```text
|S_i| = 14 - 2 - 2 = 10.                       (2)
```

The complete rooted partition is therefore four edge apexes, four
singleton classes of size ten, and 51 vertices adjacent to no anchor:

```text
4 + 4*10 + 51 = 95.
```

## 3. Consecutive singleton classes are partial matchings

Let `x in S_i`. The pair `x,a_(i+1)` is nonadjacent. It already has the
common neighbor `a_i`.

If `x` had two distinct neighbors `y,y'` in `S_(i+1)`, then both `y` and
`y'` would also be adjacent to `a_(i+1)`. The nonedge
`x,a_(i+1)` would then have the three distinct common neighbors

```text
a_i, y, y',
```

contradicting `mu=2`. Hence

```text
deg(x, S_(i+1)) <= 1.                           (3)
```

The same argument in the reverse direction shows that the bipartite graph
between `S_i` and `S_(i+1)` is a partial matching.

## 4. Exact boundary-matching sizes

The partial-matching bound can be sharpened. Recall that `t_i` is the edge
apex adjacent to `a_i,a_(i+1)`.

Fix `x in S_i`. The nonedge `x,a_(i+1)` has common neighbor `a_i` and
exactly one other common neighbor. The neighbors of `a_(i+1)`, classified
by the fixed cycle, show that the second common neighbor must lie in

```text
S_(i+1) or {t_(i+1)}.
```

The other apparent edge apex `t_i` is impossible: if `x` were adjacent to
`t_i`, then the edge `a_i t_i` would have both `a_(i+1)` and `x` as common
neighbors, against `lambda=1`. Therefore

```text
|E(S_i,S_(i+1))| + |E(S_i,{t_(i+1)})| = 10.    (4)
```

Now consider the nonedge `a_i,t_(i+1)`. One common neighbor is
`a_(i+1)`. Its second common neighbor must lie in

```text
S_i or {t_(i-1)}.
```

The candidate `t_i` is impossible because the edge `a_(i+1)t_i` already
has `a_i` as its unique common neighbor. Hence exactly one of the following
occurs:

```text
t_(i-1) is adjacent to t_(i+1),  and no S_i vertex meets t_(i+1);
t_(i-1) is nonadjacent to t_(i+1), and exactly one S_i vertex meets it.
```

Substitution in (4) gives the exact boundary size

```text
|E(S_i,S_(i+1))| =
    10, if t_(i-1) is adjacent to t_(i+1);
     9, otherwise.                              (5)
```

If `t_(i-1)` and `t_(i+1)` are adjacent, the fixed cycle anchors together
with these two apexes induce a triangular prism. Its two triangles are

```text
{t_(i-1),a_(i-1),a_i},
{t_(i+1),a_(i+1),a_(i+2)},
```

and its three matching edges are the apex edge and the two intervening
cycle edges. The fixed-cycle partition excludes every extra edge.

## 5. Cube extensions and the two prism tests

Suppose an induced cube `X` contains `C` as one of its square faces.
Label the opposite face so that `b_i` is the unique cube neighbor of `a_i`
outside `C`. Because `X` is induced, `b_i` is adjacent to `a_i` and to no
other anchor, so

```text
b_i in S_i.
```

The opposite face is the cycle

```text
b0 b1 b2 b3 b0.
```

Thus every such cube supplies a tuple in

```text
S_0 x S_1 x S_2 x S_3
```

whose consecutive entries are adjacent.

For a chosen `b0 in S_0`, equation (3) leaves at most one choice for `b1`;
that leaves at most one choice for `b2`, and then at most one for `b3`.
The final closure edge and all required nonedges can only reject the tuple,
not create additional choices. The map from an induced cube extension to
its ordered opposite-face tuple is injective. Therefore

```text
number of induced cubes having C as a face <= |S_0| = 10.   (6)
```

No converse is asserted: a tuple following the partial matchings may fail
the closure or inducedness requirements.

There are two distinct opposite pairs among the four apexes:

```text
{t_3,t_1}, {t_0,t_2}.
```

Let `tau(C)` be the number of these pairs that are adjacent, so
`tau(C)` is zero, one, or two. The four boundary matchings alternate
between the two tests in (5). A cube extension must use all four boundary
matchings. It follows that, if `e(C)` is the number of cube extensions,

```text
e(C) <= 9 + indicator[tau(C)=2].                (7)
```

## 6. Marked square--prism incidences

An adjacent opposite apex pair at `C` produces the induced triangular prism
described above. Conversely, let an induced triangular prism have base
triangles

```text
{x0,x1,x2}, {y0,y1,y2}
```

and matching edges `x_i y_i`. For each `i`, deleting the matched pair
`x_i,y_i` leaves a rectangular induced four-cycle. The deleted vertices
are the adjacent opposite edge apexes for that rectangle.

This is a bijection between:

- a square with one marked adjacent opposite apex pair; and
- a prism with one of its three matching pairs marked.

Consequently, if `P` is the number of induced triangular prisms,

```text
sum_C tau(C) = 3*P.                             (8)
```

Let

```text
D = number of squares C with tau(C)=2.
```

Every such square contributes two to the left side of (8), so

```text
2*D <= 3*P.                                     (9)
```

## 7. Six faces per cube and the final double count

Represent `Q3` by binary triples. Every four-cycle toggles two coordinates
twice and fixes the third coordinate. Choose the two toggled coordinates
and the fixed value of the remaining coordinate:

```text
C(3,2)*2 = 6.
```

Hence every induced cube contains exactly six induced four-cycles.

Count pairs `(X,C)` where `X` is an induced cube of `G` and `C` is an
induced four-cycle contained in `X`. By the cube side and (7),

```text
6*C8 = sum_C e(C)
     <= 9*2079 + D.
```

Using (9) and multiplying by two gives

```text
12*C8 <= 18*2079 + 2*D
       <= 37422 + 3*P.                          (10)
```

The independently verified identity

```text
n3 + 3*P = 4158
```

turns (10) into

```text
12*C8 <= 41580 - n3.                            (11)
```

Since `n3>=0`, equation (11) gives the unrestricted graph-class bound

```text
C8 <= 3465.
```

At the prism-free endpoint `P=0`, equivalently `n3=4158`,

```text
12*C8 <= 37422,
C8 <= floor(37422/12) = 3118.                  (12)
```

If `P` is odd, parity in (9) gives the optional one-unit strengthening
`12*C8<=37421+3P`; this is not needed for (11).

## 8. Boundary and next target

Equation (11) is global: it does not assume an automorphism or a restricted
search domain. It controls `C8` but not the signed comparison `W8-3*C8`
needed by the verified Wave 158 covariance inequality. A useful next route
is to repeat the fixed-face extension analysis for Wagner graphs and compare
their rooted extension multiplicities directly.
