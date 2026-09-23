# Binary LCD codes, forced subset words, and the ordinary-enumerator wall

Claim labels: `DERIVED` for the conditional finite counts,
`CANDIDATE` for the rational witness, and `UNKNOWN` beyond the declared
ordinary system.

## 1. Symmetric idempotent codes

Reducing

```text
A^2 = 12I-A+2J
```

modulo two gives `A^2=A`.  Since `A` is symmetric,

```text
C=im(A),       D=ker(A)=C^perp,
F2^99=C direct_sum D.
```

Thus both codes are LCD.  Every row of `A` has even weight 14, so `C` is
even.  The standard dot product restricted to `C` is therefore alternating
and nondegenerate: `C` is a 54-dimensional binary symplectic space.

The all-one vector lies in `D` because every graph degree is even.  Hence
the dual enumerator has complement symmetry

```text
B_w=B_(99-w).                                         (1)
```

## 2. The two injective subset maps

For a vertex subset `S`, write `x_S` for its indicator.  Define

```text
f(S)=A x_S in C,
g(S)=(I+A)x_S in D,
```

where `A(I+A)=A+A^2=0`.

If `f(S)=f(T)`, then `x_(S symmetric_difference T)` lies in `D`.  For
`|S|,|T|<=3`, it has weight at most six.  The verified lower bound
`d(D)>=8` forces `S=T`.  The same argument for `g`, using
`ker(I+A)=im(A)` and `d(C)>=8`, proves:

```text
f and g are injective on all subsets of size at most 3.       (2)
```

This includes injectivity across different subset sizes and graph types.

## 3. One- and two-vertex words

For one vertex, `f` is its weight-14 neighborhood and `g` its weight-15
closed neighborhood.

For a pair, `f` is the symmetric difference of two neighborhoods.
Adjacent vertices have one common neighbor; nonadjacent vertices have two.
Toggling the two endpoints gives the `g` weights:

| subset | count | `wt f(S)` | `wt g(S)` |
|---|---:|---:|---:|
| one vertex | 99 | 14 | 15 |
| edge | 693 | 26 | 24 |
| nonedge | 4,158 | 24 | 26 |

## 4. Exact three-set split

Let `S` have three vertices, `e` induced edges, and let `c` be the number
of graph vertices adjacent to all three members of `S`.  If
`t_v=|N(v) intersection S|`, then

```text
sum_v t_v = 42,
sum_v binom(t_v,2) = 6-e.
```

Writing `n_i=#{v:t_v=i}` and eliminating `n_1,n_2` gives

```text
wt f(S)=n_1+n_3=30+2e+4c.                           (3)
```

To pass from `f` to `g`, toggle the three coordinates of `S`.  The number
already present is the number of vertices of odd degree in the induced
three-vertex graph.  This adds three for independent triples and triangles,
and subtracts one for one-edge triples and paths.

The counts are:

- triangles: `693/3=231`;
- induced paths: each center chooses a nonedge of its `7K2` neighborhood,
  giving `99*(C(14,2)-7)=8,316`;
- one-edge triples: each edge has 72 vertices meeting neither endpoint.
  Twelve meet its unique triangle vertex, giving `8,316`; the remaining
  sixty give `41,580`;
- independent triples: subtracting the preceding types from `C(99,3)`
  gives `98,406`.  A common neighbor chooses one vertex from each of three
  matched pairs in its `7K2` neighborhood, giving
  `99*C(7,3)*2^3=27,720`.  Two common neighbors are impossible because
  any pair of vertices has at most two common neighbors, fewer than the
  three vertices they would both need to meet.  Hence the remaining
  `70,686` have no common neighbor.

Substitution in (3) gives:

| three-set type | count | `c` | `wt f` | `wt g` |
|---|---:|---:|---:|---:|
| independent | 70,686 | 0 | 30 | 33 |
| independent | 27,720 | 1 | 34 | 37 |
| one edge | 41,580 | 0 | 32 | 31 |
| one edge | 8,316 | 1 | 36 | 35 |
| induced path | 8,316 | 0 | 34 | 33 |
| triangle | 231 | 0 | 36 | 39 |

By (2), all displayed words are distinct.  Aggregating equal weights gives
the forced tables recorded in `exact-results.json`.

## 5. Exact rational ordinary MacWilliams witness

Let `A_i` and `B_j` denote the weight enumerators of `C` and `D`.
The binary MacWilliams equations are

```text
B_j = 2^-54 sum_i A_i K_j(i),                       (4)
```

where `K_j(i)` is the binary Krawtchouk polynomial for length 99.

The stored witness imposes:

- `A_0=B_0=1`, `sum A_i=2^54`, `sum B_j=2^45`;
- `A_i=0` for odd `i` and for `1<=i<=13`;
- `B_j=0` for `1<=j<=14`;
- all forced lower bounds and (1);
- nonnegativity of every coefficient.

All 100 forward equations (4) and all 100 inverse equations replay exactly
with rational arithmetic.  The witness therefore permits ordinary
enumerator distances `(14,15)`.

It has 34 nonintegral image coefficients and 32 nonintegral dual
coefficients.  It is only a rational point in the ordinary MacWilliams
polytope.

## 6. Integral scout and next boundary

The stricter system makes every `A_i,B_j` integral and includes all 100
MacWilliams equations.  A fresh worker received a ten-second solver timeout
and a hard 15-second parent wall.  The parent killed the still-running
worker and recorded `UNKNOWN_HARD_TIMEOUT`.  This supplies no evidence
either way.

Ordinary coefficients forget the main graph datum.  If `r_v` is the
neighborhood row and `q_v=e_v+r_v` the closed-neighborhood row, then over
`F2`

```text
<r_u,r_v> = (A^2)_uv = A_uv,
<q_u,q_v> = ((I+A)^2)_uv = (I+A)_uv,
<r_u,q_v> = (A(I+A))_uv = 0.                        (5)
```

Thus the unknown graph is the symplectic Gram matrix of 99 distinguished
weight-14 words, while 99 distinguished weight-15 dual words have Gram
`I+A`.  Joint or split enumerators retaining the labelled systems in (5)
are the next meaningful code-theoretic layer.

No code or graph is constructed, and Conway-99 remains `UNKNOWN`.
