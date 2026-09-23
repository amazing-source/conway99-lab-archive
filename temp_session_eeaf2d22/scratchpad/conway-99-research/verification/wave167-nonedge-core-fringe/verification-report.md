# Wave 167 clean-room audit

## Verdict

The core/fringe decomposition, completion uniqueness, and global defect
arithmetic are `VERIFIED_WITH_SCOPE`. The bound `E<=8` remains `UNPROVED`.

## 1. Cross graph

Fix nonedge `uv` with common neighbors `p,q`. Let `a,c` be the edge
triangle mates on `up,uq`, and `b,d` those on `vp,vq`. With

```text
R=N(u)\{p,q,a,c}, S=N(v)\{p,q,b,d},
```

both sets have size ten.

For any `alpha in N(u)\{p,q}`, the two common neighbors of `alpha,v`
are exhausted by its incidences with `p,q` and its neighbors in
`N(v)\{p,q}`. Thus `a,c` have cross degree one and every vertex of `R`
has cross degree two. Symmetry gives the same degree sequence on the other
side, so the cross graph has 22 edges.

The pairs `a-b,c-d` are excluded by `lambda=1`. The pairs `a-d,c-b`
would join the apexes of opposite edges of the induced square
`u-p-v-q-u` and create an induced triangular prism. They are absent at
`P=0`.

Verdict: `VERIFIED`.

## 2. Core/fringe split

The `p` and `q` lanes each contain 20 cross edges. Their union is the full
22-edge cross graph and their intersection is `E(R,S)`. Therefore

```text
|E(R,S)|=20+20-22=18.
```

Every core edge is present in both lanes, yielding 36 core marks. Cross
degree one at each apex leaves exactly four fringe edges, one each of types

```text
a-S, c-S, R-b, R-d.
```

They yield four fringe marks.

Verdict: `VERIFIED`.

## 3. Mandatory failures

In the `p` lane, a fringe through `c` or `d` forces the other
pair-support vertex to be `q`; `q` has an extra marked-cycle neighbor. In
the `q` lane, a fringe through `a` or `b` similarly forces `p`. Each
support is impure, so all four fringe marks fail.

This proves

```text
f(uv)>=4,
```

not `f(uv)<=4`.

Verdict: `VERIFIED`.

## 4. Completion multiplicity

For a pure successful mark, the required pair-support vertex `r` is
nonadjacent to the marked middle `p`. They have exactly two common
neighbors. One is the cycle vertex `u`, so the completion vertex is uniquely
the other. Hence a mark has zero or one valid completion.

Conversely, the support pattern of the three vertices outside an induced
five-cycle in a Wagner graph is `2,1,2`; its unique singleton support selects
one mark. A Wagner graph has eight induced five-cycles. Therefore successful
marks are counted exactly eight times per Wagner graph.

With 4,158 nonedges and 40 marks per nonedge,

```text
F=4158*40-8*W8=166320-8*W8.
```

No orientation or completion multiplicity is missing.

Verdict: `VERIFIED`.

## 5. Defect gap

Four mandatory failures per nonedge give `B0=16632`. Therefore

```text
E=F-B0=149688-8*W8=8*(18711-W8).
```

In particular, `E` is nonnegative and divisible by eight. At `P=0`, the
previously verified bounds `C8<=3118` and

```text
37422+12*C8-4*W8>=0
```

give the integer bound `W8<=18709`, so `E>=16`.

Consequently `E<=8` would exclude the endpoint. Pointwise equality
`f(uv)=4` would imply the stronger conclusion `E=0`.

Verdict: `VERIFIED`.

## 6. Hostile local-shell test

The explicit shell in the attempt has:

- four fringe edges;
- 18 core edges;
- degree one at each apex;
- total cross degree two at each ordinary vertex; and
- no apex-apex edge.

Direct degree inspection confirms these facts. Its four distinct ordinary
fringe endpoints retain core incidences, making at least four core marks
impure in addition to the mandatory fringe failures.

The shell is not a full SRG and therefore does not refute `E<=8` for a
hypothetical target graph. It does prove that the displayed one-root
equations and root-visible prism exclusions are insufficient.

Verdict: `VERIFIED_WITH_SCOPE`.

## Boundary

The next proof must add cross-root compatibility, a complete exact conic
dual, or another genuinely higher-order invariant. No such proof is present
in this package. The rigorous interval remains `708<=n3<=4158`.
