# Wave 166 clean-room audit

## Verdict

The rooted-space reductions are `VERIFIED_WITH_SCOPE`. The decisive
four-failure lemma remains `UNPROVED`.

## Fixed-square shell

For `x in U_i`, consecutive-class degrees are zero or one. Exhausting the
two common neighbors of `x,v_(i+2)` gives

```text
deg(x,U_(i+2))
  = deg(x,U_(i-1)) + deg(x,U_(i+1)).
```

At `P=0`, each consecutive matching has nine edges, so every opposite-class
graph has exactly 18 edges and maximum degree two. The three possible
four-cycles on the labelled outside vertices are one cube pattern and two
Wagner patterns.

The abstract shell with identity consecutive matchings on `Z/9`, opposite
shift sets `A={0,1}` and `B={2,3}`, and one inactive vertex per class
satisfies all these equations. Both `A intersect B` and
`A intersect (-B)` are empty, so it has no crossed Wagner. This correctly
proves that the shell equations alone force no Wagner lower bound. It is not
an SRG completion.

## Exactly forty marked five-cycles per nonedge

Fix nonedge `uv` with common neighbors `p,q`, and choose `p` as the marked
middle. Let `a,b` be the edge apexes on `up,vp`. Let `X` be the neighbors
of `u` nonadjacent to `v,p`, and define `Y` symmetrically.

The exact neighborhood partitions are

```text
N(u)={p,q,a} disjoint_union X,
N(v)={p,q,b} disjoint_union Y,
|X|=|Y|=11.
```

For `x in X`,

```text
deg(x,Y)=2-indicator[x~q]-indicator[x~b].
```

Both `q` and `b` have exactly one neighbor in `X`; these exceptional
neighbors may coincide, but their incidence sum is two. Hence

```text
|E(X,Y)|=22-1-1=20.
```

Edges `xy` are in bijection with induced cycles `u-p-v-y-x-u`.
The `q` lane supplies another disjoint 20, so every nonedge has exactly 40
marked induced `C5`s. The global check is

```text
4158*40=166320=5*33264.
```

No orientation factor is missing.

## Wagner completion and endpoint implication

For a marked cycle, the second common neighbors `r` of `u,y` and `s` of
`v,x`, together with a singleton-supported common neighbor `z`, induce a
Wagner graph when the exact-support and `r,s` nonedge checks pass.
Conversely, the three vertices outside a `C5` in a Wagner form a path whose
middle has a unique cycle neighbor, selecting one marked diagonal.

Every Wagner contains eight induced `C5`s, so completed incidences total

```text
8*W8.
```

If every nonedge had at most four failed marks, there would be at least

```text
4158*36=149688
```

successful marks. Thus `W8>=18711`. With the verified endpoint
`C8<=3118`,

```text
W8-3*C8>=9357,
```

contradicting the endpoint covariance bound `W8-3*C8<=9355`.

## Why the decisive lemma is still open

For one common-neighbor lane, at most two marked cycles have an impure `r`
and at most two have an impure `s`; hence at most four are visibly impure.
There are two lanes. Moreover, a pure pair can still lack the required
singleton-supported completion. The current equations neither force that
completion nor couple the two lanes from eight possible failures down to
four.

Therefore

```text
P=0 => f(uv)<=4
```

is not proved.

## Exact conic boundary

The verified Wave 150 pseudowitness has

```text
C8=11781/4,
W8=35343/2.
```

It has slack 2,079 in both endpoint scalar inequalities and lies on the
pair-root centered PSD face. Consequently, pair-root order-eight PSD plus
the new scalar bounds cannot prove `W8>=18710`. A successful exact
order-eight dual must use the whole root-3/root-12 blocks; otherwise marked
completion second moments naturally lift to order eleven.

No strict `n3` bound or Conway-99 conclusion is promoted.
