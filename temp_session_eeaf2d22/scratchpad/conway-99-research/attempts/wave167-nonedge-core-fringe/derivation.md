# Derivation

Let `G` be a hypothetical `srg(99,14,1,2)`. Thus every vertex has degree
14, every adjacent pair has exactly one common neighbor, and every
nonadjacent pair has exactly two common neighbors. Let `P` be the number of
induced triangular prisms and work under the endpoint assumption `P=0`.

## 1. Cross graph at a fixed nonedge

Fix nonadjacent vertices `u,v`, whose common neighbors are `p,q`. Let

```text
a = the unique triangle mate of edge up,
c = the unique triangle mate of edge uq,
b = the unique triangle mate of edge vp,
d = the unique triangle mate of edge vq.
```

Set

```text
R = N(u) \ {p,q,a,c},
S = N(v) \ {p,q,b,d}.
```

Then `|R|=|S|=10`. Put `A={a,c} union R` and `B={b,d} union S`.

Every vertex of `A` is nonadjacent to `v`. Exhausting its two common
neighbors with `v` gives its degree into `B`. The apexes `a,c` have cross
degree one, while every vertex of `R` has cross degree two. The same holds
on the other side. Therefore the bipartite cross graph `G[A,B]` has degree
sequence

```text
1,1,2,2,2,2,2,2,2,2,2,2
```

on each side and exactly 22 edges.

The edges `a-b` and `c-d` are forbidden by `lambda=1`. For example, `a-b`
would give the adjacent pair `p,a` two common neighbors, `u` and `b`.

The edges `a-d` and `c-b` are forbidden by `P=0`: either edge, together with
the two opposite edge-apex triangles on the induced square
`u-p-v-q-u`, creates an induced triangular prism. Hence there are no
apex-apex cross edges.

## 2. Eighteen core edges and four fringe edges

The `p` lane of marked cycles

```text
u-p-v-y-x-u
```

uses cross edges between `{c} union R` and `{d} union S` and has exactly
20 edges. The `q` lane uses cross edges between `{a} union R` and
`{b} union S` and also has 20 edges.

The union of the lane edge sets is the full 22-edge cross graph, and their
intersection is exactly `E(R,S)`. Inclusion-exclusion gives

```text
40 = 22 + |E(R,S)|,
```

so

```text
|E(R,S)| = 18.
```

Each core edge in `E(R,S)` belongs to both lanes and yields two marked
cycles, for 36 core marks. The remaining four cross edges are exactly one
of each type

```text
a-S, c-S, R-b, R-d,
```

and yield four fringe marks.

## 3. The four fringe marks fail

For a marked cycle `m=(u,p,v,y,x)`, let

```text
r = the common neighbor of u,y other than x,
s = the common neighbor of v,x other than y.
```

If a `p`-lane fringe has `x=c`, then `s=q`; if it has `y=d`, then `r=q`.
In either case `q` has an extra neighbor on the marked cycle, so the
required support is impure. In the `q` lane, the `a-S` and `R-b` fringes
similarly force the impure vertex `p`. All four fringe marks therefore fail.

This establishes only

```text
f(uv) >= 4.
```

## 4. Completion uniqueness

Suppose a marked cycle is pure and admits a Wagner completion. The required
pair-support vertex `r` is nonadjacent to the marked middle vertex `p`.
Because `mu=2`, the pair `r,p` has exactly two common neighbors. One is
already `u`; hence the required completion vertex `z` is the unique other
common neighbor. A successful mark therefore has exactly one completion,
not several.

Conversely, relative to any induced five-cycle in an induced Wagner graph,
the three outside vertices have cycle-support sizes `2,1,2`. The unique
singleton support selects the marked diagonal and its canonical completion.
Every induced Wagner graph has eight induced five-cycles, so the number of
successful marks is exactly `8*W8`.

There are `4158*40=166320` total marks. Consequently

```text
F = 166320-8*W8.
```

## 5. Global defect gap

The mandatory fringe baseline is

```text
B0 = 4*4158 = 16632.
```

Define

```text
E = F-B0.
```

Then

```text
E = 149688-8*W8 = 8*(18711-W8).
```

Thus `E>=0` and `E` is divisible by eight.

At `P=0`, Wave 165 gives `C8<=3118`. The verified covariance inequality

```text
37422+12*C8-4*W8 >= 0
```

then gives `W8<=18709`. Hence the endpoint requires `E>=16`.

It follows that either of these would exclude the endpoint:

```text
E <= 8                                      (global sufficient target),
f(uv)=4 for every nonedge uv                (stronger pointwise target).
```

The first target allows one unit of eight in the global defect and is the
sharper continuation.

## 6. Local shell obstruction

The currently derived local constraints do not force the pointwise target.
One abstract cross-shell is:

```text
R={r0,...,r9}, S={s0,...,s9},
fringe: a-s0, c-s1, r0-b, r1-d,
core seeds: r2-s0, r3-s1, r0-s2, r1-s3,
paths:
  r2-s4-r4-s5-r5-s2,
  r3-s6-r6-s7-r7-s8-r8-s9-r9-s3.
```

Every apex has cross degree one, every ordinary vertex has total cross
degree two, the shell has 22 cross edges and 18 core edges, and all
root-visible apex-apex exclusions hold. The distinct fringe endpoints make
at least four core marks impure in addition to the four fringe failures.

This is not a full SRG completion. Its role is narrower: a proof of
`E<=8` must use constraints that couple this shell to other roots or to
higher-order completion data.
