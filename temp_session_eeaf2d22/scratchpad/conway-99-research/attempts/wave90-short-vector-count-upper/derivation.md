# A rooted transition bound for the norm-14 shell

Claim label: `DERIVED` (independent verification required).

Everything is conditional on the frozen protocol, in particular the
prism-free endpoint.

## 1. The rooted scaffold

Fix a graph vertex `o`. Its 14 neighbors form seven disjoint mate edges.
Every vertex nonadjacent to `o` is the unique second common neighbor of a
nonmate pair in `N(o)`. Thus the 84 residual vertices are labelled by the
edges of

```text
H = K14 - 7K2.
```

At each base point `s`, the twelve residual labels incident with `s` are
paired by six selected transition edges. Prism-freeness says that the two
other endpoints in a selected transition are not mates.

## 2. A norm-14 vector gives a four-point seed

Let `t` be a norm-14 vector with `t_o=+1`. The negative sign side is
independent and exactly four of its vertices neighbor `o`. Call this
four-set `Q`. It contains at most one endpoint from each root mate pair, so
there are

```text
C(7,4) * 2^4 = 560
```

possible seeds.

For every pair `{a,b}` in `Q`, the vertices `a,b` are nonadjacent and have
the two common neighbors `o` and the residual label `{a,b}`. The
complementary-Fano support saturates this pair, so all six residual labels
`C(Q,2)` are the other six positive support vertices. They must be
independent. In particular, no selected transition can join two of them.

The map from a rooted vector to `Q` is injective. Indeed, `Q` determines the
six other positive vertices. Every positive-side pair then has both of its
common graph neighbors on the negative side, and the union of these common
neighbor pairs is exactly the seven-point negative side. Hence `Q`
determines both sign sides and therefore `t`.

## 3. Transition-seed double counting

There are

```text
14 * 6 = 84
```

selected transitions. Write one as

```text
{s,a} -- {s,b}.
```

The three base points `s,a,b` lie in distinct mate groups: each residual
label avoids a mate pair, and prism-freeness excludes `a,b` being mates.
To extend them to a seed `Q`, choose one endpoint from one of the four
remaining mate groups. Therefore every selected transition lies in exactly

```text
4 * 2 = 8
```

seeds. The number of transition-seed incidences is consequently

```text
84 * 8 = 672.
```

Inside one seed, fix one of its four base points `s`. The three residual
labels through `s` meet a perfect matching, so at most one of their three
pairs is a selected transition. Summing over the four base points, a seed
contains at most four selected transitions.

Therefore at least

```text
672 / 4 = 168
```

of the 560 seeds contain a transition. At most

```text
560 - 168 = 392
```

seeds can arise from a rooted norm-14 vector.

## 4. Global count and signs

For every root `o`,

```text
#{t : ||t||^2=14 and t_o=+1} <= 392.
```

The shell count `N14` includes both signs. Every vector has exactly seven
positive coordinates, so summing over all 99 possible roots counts every
oriented vector exactly seven times:

```text
7*N14
 = sum_o #{t : ||t||^2=14 and t_o=+1}
 <= 99*392.
```

Since `392=7*56`,

```text
boxed: N14 <= 99*56 = 5544.
```

## Boundary

The provisional Wave 86 theorem concerns
`N14+N16+N18`, not `N14` alone. Norm-16 and norm-18 vectors can absorb
transition adjacencies through their deficiency patterns, so the present
argument does not bound those two shells. No contradiction or target
resolution is claimed.

