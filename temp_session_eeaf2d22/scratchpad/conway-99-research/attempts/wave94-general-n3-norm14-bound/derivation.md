# Prism-sensitive rooted upper bound for `N14`

Claim label: `DERIVED` (independent verification required).

## 1. Rooted prism transitions

Fix a vertex `o`. Its neighborhood is seven mate edges. The 84 residual
vertices are the nonmate pairs of the 14 base vertices. At every base point
`s`, the twelve incident residual labels are paired into six selected
transitions, for 84 selected transitions in total.

Call a selected transition

```text
{s,a} -- {s,b}
```

`mate-forbidden` when `a,b` are mates. It then gives the induced triangular
prism with triangles

```text
{o,a,b} and {s,{s,a},{s,b}}.
```

Conversely, an induced prism containing `o` has a unique opposite vertex
`s` matched to `o`, and its other two matching edges recover exactly one
mate-forbidden transition. Thus, if `f_o` is the number of mate-forbidden
transitions rooted at `o`, then

```text
f_o = number of induced prisms containing o.
```

Every prism has six vertices, so

```text
sum_o f_o = 6P.                                      (1)
```

## 2. Seed incidence with prisms retained

A norm-14 vector with `t_o=+1` injects into a four-point seed `Q` choosing
one endpoint from four of the seven mate groups. There are

```text
C(7,4)*2^4 = 560
```

seeds.

A mate-forbidden transition lies in no seed because a seed cannot contain
both endpoints of one mate edge. Every one of the other `84-f_o` selected
transitions has three base points in distinct mate groups and lies in
exactly eight seeds.

Hence the transition-seed incidence count at root `o` is

```text
8*(84-f_o).
```

At each one of a seed's four base points, the local transition relation is a
matching, so the seed contains at most four selected transitions. Therefore
at least

```text
8*(84-f_o)/4 = 168-2*f_o
```

seeds are bad, and at most

```text
560-(168-2*f_o) = 392+2*f_o                   (2)
```

are transition-free.

The complementary-Fano saturation argument makes the rooted seed map
injective and forces a norm-14 seed to be transition-free. Thus (2) bounds
the number of norm-14 vectors with `t_o=+1`.

## 3. Global count

Every oriented norm-14 vector has exactly seven positive coordinates.
Summing (2) over all 99 roots and using (1) gives

```text
7*N14
 <= sum_o (392+2*f_o)
 = 99*392 + 2*6P
 = 38808+12P.
```

Since `N14` is integral,

```text
N14 <= floor((38808+12P)/7).                         (3)
```

The verified identity `n3+3P=4158` turns (3) into

```text
boxed: N14 <= floor((55440-4*n3)/7).                 (4)
```

The endpoint values include:

| `n3` | `P` | upper bound on `N14` |
|---:|---:|---:|
| 4158 | 0 | 5544 |
| 4155 | 1 | 5545 |
| 708 | 1150 | 7515 |
| 0 | 1386 | 7920 |

At `P=0`, (3) specializes to the sealed Wave90 discovery theorem.

## Boundary

The slope in (4) is a genuine global bridge between the prism count and one
short lattice shell. The scalar lower bound concerns three shells, however.
Norm-16 and norm-18 deficiency patterns remain unbounded here, so no
contradiction or strict `n3` upper bound follows.

