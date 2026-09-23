# Universal short cross-star relations

## 1. Adjacent stars

Work conditionally in the verified Wave 176 rank-11 endpoint model.  Let
`x~y`, let `T0` be the common triangle block, and impose coefficient zero
at `T0` on the true relation space of the 13 union columns.  Puncturing that
zero coordinate gives a ternary relation code `R_xy` on the 12 outer
columns.

Wave 176 gives relation dimension at least three before imposing the zero
coordinate, hence

```text
k=dim(R_xy)>=2.
```

The difference of the two seven-star circuits cancels at `T0` and gives

```text
s0=(1 on the six x-outer blocks, -1 on the six y-outer blocks).
```

Thus `S0=<s0>` is a one-dimensional subcode of `R_xy`.  It has two nonzero
words, both of weight 12.  Every coordinate of `R_xy` is active because it
is nonzero in `s0`.

In a full-support ternary `[n,k]` code, each coordinate is nonzero in
`2*3^(k-1)` words.  Therefore the sum of all weights in `R_xy` is

```text
12*2*3^(k-1).
```

Remove the three words of `S0`, whose total weight is 24.  Every remaining
word is genuinely cross-star: the only combinations of the two individual
star circuits whose `T0` coefficient vanishes are the words of `S0`.
Their exact average weight is

```text
(24*3^(k-1)-24)/(3^k-3)=8.                        (1)
```

At least one genuine cross-star relation therefore has weight at most
eight.  Wave 174 gives dual distance at least four, proving the universal
range

```text
4..8.                                             (2)
```

It avoids `T0`.  Pairing its column relation with `z_T0` shows its
coefficient sum is zero, since every outer column has inner product one
with `z_T0`.  Hence (2) also holds after replacing centered columns
`z_T` by the uncentered columns `v_T=z_T+w`.

## 2. Nonadjacent stars

For nonadjacent `x,y`, the two stars are disjoint.  Their 14-column true
relation code `R` has dimension `k>=3`.  Let `S` be the two-dimensional
span of the two individual star circuits.  Again every coordinate is
active.

The total weight over `R` is

```text
14*2*3^(k-1).
```

Inside `S`, two words are supported on each individual seven-star and four
words are supported on both.  Its total weight is

```text
2*7+2*7+4*14=84.
```

After removing the nine words of `S`, every remaining word is genuinely
cross-star and the exact average is

```text
(28*3^(k-1)-84)/(3^k-9)=28/3.                    (3)
```

Some integer weight is therefore at most nine.  Dual distance again gives

```text
4..9.                                             (4)
```

## 3. The type `4+2` relation is a plane conic

Wave 176 proves that adjacent cycle type `4+2` has a true weight-four
relation.  Multiply each of its four supported centered columns by its
nonzero relation coefficient.  The resulting vectors `u_1,...,u_4`
satisfy

```text
sum_i u_i=0,
Gram(u_1,...,u_4)=J_4-I_4.
```

The Gram matrix has rank three.  The four vectors span a nondegenerate
three-space, all are singular, and a nondegenerate conic in `PG(2,3)` has
exactly four points.  They are therefore the complete conic `Q(2,3)`.

For the rank-one self-adjoint operators `u tensor u`,

```text
sum_(u in Q(2,3)) u tensor u=-I.                  (5)
```

Indeed, applying the left side to any conic vector and using the simplex
Gram gives `-u`.

There are 13 points in `PG(2,3)`.  The outer-product sum over all 13 is
zero over `F_3`: equivalently, sum over all nonzero vectors first, where
each diagonal coordinate occurs nonzero 18 times and every mixed sum
vanishes, then divide by the two representatives of each point.  The nine
nonconic points consequently contribute

```text
+I.                                               (6)
```

Equations (5)--(6) are an exact hostile control.  The local conic is fully
compatible with the zero-frame/3-divisibility equation, so that equation
alone cannot exclude type `4+2`.

## Boundary

Every one of the 693 edges indexes at least one true relation of weight at
most eight, and every nonedge indexes one of weight at most nine.  The same
relation may be indexed by more than one pair; no distinctness or global
multiplicity is claimed.  Exclusion now requires a theorem controlling
overlap or circuit elimination across many stars, not another local
dimension count.  No rank-11 contradiction, strict `n3` improvement,
graph construction, or Conway-99 resolution follows.
