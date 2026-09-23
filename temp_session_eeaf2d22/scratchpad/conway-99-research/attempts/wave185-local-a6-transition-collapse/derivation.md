# Local A6 transition collapse

## 1. Frozen equality setting

Assume the independently verified Wave 181--184 equality setting.  Fix a
graph vertex `x`.  Its 14 neighbors induce seven disjoint edges

```text
V_i={i_0,i_1}, 1<=i<=7.
```

Every nonneighbor `y` of `x` is uniquely labelled by its two common
neighbors with `x`:

```text
y=y_(i_alpha,j_beta), i!=j.
```

For the local projective `A6` root `e={i,j}`, let

```text
Y_e={y_(i_alpha,j_beta): alpha,beta in {0,1}}.
```

The 21 four-sets `Y_e` partition the 84 nonneighbors of `x`.  Wave 183 says
that, according as the global root containing `e` has multiplicity 5, 6, or
7,

```text
G[Y_e]=4K1, 2K2, or P4.                           (1)
```

## 2. An induced prism forbids same-endpoint cell edges

Suppose two vertices in `Y_{ij}` sharing their actual `V_i` endpoint were
adjacent:

```text
y=y_(i_alpha,j_0) ~ y'=y_(i_alpha,j_1).
```

Then

```text
{i_alpha,y,y'} and {x,j_0,j_1}
```

are disjoint graph triangles.  They have the three cross edges

```text
x i_alpha, j_0 y, j_1 y'.
```

There are no other cross edges.  The vertex `x` is nonadjacent to `y,y'`;
the local graph at `x` has no edges between different mate pairs; and an
extra edge `j_0 y'` or `j_1 y` would give the edge `j_0j_1` a second common
neighbor besides `x`.  The six vertices would therefore induce a triangular
prism, contrary to the endpoint condition `P=0`.

The same argument applies at the `V_j` endpoint.  Hence an internal edge can
only join one of the two opposite-corner pairs

```text
(i_0,j_0)--(i_1,j_1),
(i_0,j_1)--(i_1,j_0).                             (2)
```

Those edges are disjoint, so every `G[Y_e]` has maximum degree at most one.
The `P4` possibility in (1) is impossible:

```text
n_7=0.                                            (3)
```

## 3. Exact transition table

The graph induced by the 84 nonneighbors of `x` is 12-regular.  A rooted
label has exactly two neighbors whose labels share an actual endpoint, one
at each endpoint, and ten neighbors with disjoint actual labels.

Let `d_e(y)` be the internal degree of `y` in `Y_e`.  The rooted
common-neighbor profile says that the total number of neighbors of `y` in
cells whose root contains `i` is two, and likewise for `j`.  An internal
neighbor is counted in both totals, so the off-diagonal degree into the ten
cells incident with `e` in `L(K7)` is

```text
4-2*d_e(y).                                       (4)
```

The two actual-endpoint transitions occur there and, by Section 2, are not
internal.  Subtracting them, and then using the ten disjoint-label
neighbors, gives:

| global type | internal | incident transition | incident disjoint | orthogonal |
|---|---:|---:|---:|---:|
| `m=5` | 0 | 2 | 2 | 8 |
| `m=6` | 1 | 2 | 0 | 9 |

Thus a type-five cell sends 8 transition edges and 8 disjoint-label edges
to incident cells; a type-six cell sends 8 transition edges and no
disjoint-label edge to incident cells.

## 4. Incident-cell capacity

For incident roots `e={i,j}` and `f={i,k}`, let `b_ef` count graph edges
between `Y_e,Y_f` whose actual labels are disjoint.  Such an edge must choose
opposite actual endpoints in `V_i`.

For either orientation in `V_i`, the possible pairs form a `K_{2,2}`.  All
four cannot occur: the two vertices on one side already share their base
endpoint, and the two vertices on the other side would then give them two
additional common neighbors, exceeding `mu=2`.  Each orientation contributes
at most three, hence

```text
b_ef<=6.                                          (5)
```

The transition table gives

```text
sum_(f incident e) b_ef =
  8 if e has type five,
  0 if e has type six.                            (6)
```

By symmetry, a nonzero `b_ef` joins two type-five roots.  Equations (5)--(6)
make the underlying simple companion graph at a type-five local root have
degree at least two.

## 5. Global type-five companions

Fix a multiplicity-five root `r`.  Its support `X_r` is a five-coclique.
At each `x in X_r`, Section 4 supplies at least two other type-five roots
through `x`.

Companions obtained at two different support vertices are distinct.  If
another root `s` occurred with `r` at two vertices `x,x' in X_r`, then
`x,x'` would be a graph nonedge and

```text
s in R_x intersect R_x'={r},
```

contradicting `s!=r`.  Every type-five root therefore has at least ten
distinct type-five companions, so

```text
n_5>=11.                                          (7)
```

With (3), the global root-incidence equation becomes

```text
5*n_5+6*n_6=2079.                                 (8)
```

Modulo six, `n_5=3 mod 6`.  Combining this with (7),

```text
n_5>=15,
(n_5,n_6)=(15+6u,334-5u), 0<=u<=66.              (9)
```

Consequently

```text
|mathcal R|=n_5+n_6=349+u,
349<=|mathcal R|<=415.                            (10)
```

The lower endpoint is only arithmetically feasible; no configuration is
asserted.

## 6. Two useful shadows

The characteristic-three root-frame identity reduces to

```text
sum_(m_r=5) r tensor r=0.                         (11)
```

Thus the type-five roots generate a projective ternary self-orthogonal code.
No current bound for that code excludes the lengths in (9).

In the complement graph, every triangle is monochromatic or rainbow.  With
only type-five and type-six colors, the monochromatic count is

```text
10*n_5+8*n_6=4158-4*n_6<=4142,
```

so at least

```text
98406-4142=94264
```

complement triangles are rainbow.  This large rainbow count does not meet
the hypotheses of the checked Gallai-type nonexistence theorems.

## Boundary

The multiplicity-seven branch is excluded and the conditional root interval
improves from `297..415` to `349..415`.  The surviving weighted `L(K7)`
transition systems and the type-five self-orthogonal code remain feasible at
the proved level.

No strict `n3` improvement, rank-11 exclusion, graph construction, or
Conway-99 resolution follows.
