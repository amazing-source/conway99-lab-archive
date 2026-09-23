# Source-blind derivation of the two-center five-slot theorem

## Statement and scope

Work conditionally in the independently verified prism-free rank-11
endpoint framework.  Fix a selected exact-three nonedge label

```text
e={x,y}.
```

Let `m_(x->y)` and `m_(y->x)` be the numbers of selected canonical
exact-three flags in the two orientations.  Then

```text
m_(x->y)+m_(y->x)<=5.                            (1)
```

The argument uses no construction or search.  It is a two-center gluing
argument in the ternary relation matroid.

## 1. The two five-element slot sets

The nonedge `xy` has exactly two common neighbors, say `a,b`.  They are
nonadjacent: otherwise the edge `ab` would have the two common neighbors
`x,y`, contrary to `lambda=1`.

Let

```text
X_a, X_b
```

be the graph-triangle blocks through the edges `xa,xb`, and let

```text
Y_a, Y_b
```

be those through `ya,yb`.  The two blocks in each endpoint star are
distinct, because `a,b` are nonadjacent.  Delete `X_a,X_b` from the
seven-block `x`-star and `Y_a,Y_b` from the seven-block `y`-star:

```text
L_x(e)=S_x minus {X_a,X_b},
L_y(e)=S_y minus {Y_a,Y_b}.
```

Both sets have size five.  Every block in `L_x(e)` is anticomplete to
`y`: its two non-`x` vertices are neighbors of `x` other than the only
two common neighbors `a,b`.  Symmetrically every block in `L_y(e)` is
anticomplete to `x`.

## 2. A partial third-block injection

Take an `x->y` flag `(x,T)`.  The leaf triangle `T` belongs to `L_y(e)`.
The verified leaf-type theorem says that the two blocks of `A_x(T)`
recording the type of leaf `y` are exactly `X_a,X_b`.  Since
`|A_x(T)|=3`, there is a unique third block

```text
sigma_x(T)=S in L_x(e),
A_x(T)={X_a,X_b,S}.                              (2)
```

This partial map is injective on the selected flags.  If two flags had
the same `S`, their `A_x` sets would be equal.  Fixed-center
`A`-injectivity, which follows by subtracting the two globally normalized
flag relations and invoking dual distance at least four, then gives the
same leaf triangle and the same canonical flag.

Thus the `x->y` flags occupy distinct elements of the five-element set
`L_x(e)`.

A reverse `y->x` flag `(y,S)` has its leaf triangle `S` in the same set
`L_x(e)`.  The center and leaf triangle determine its canonical flag, so
distinct reverse flags also occupy distinct elements of `L_x(e)`.

It remains to prove that a forward and reverse flag cannot occupy the
same slot.

## 3. Reverse leaf-type matching

Suppose `(x,T)` has third block `S` as in (2), and suppose the reverse
flag `(y,S)` is also selected.  By definition of `A_x(T)`,

```text
j(S,T)=2,                                        (3)
```

where `j` is the number of graph cross edges between the two triangle
blocks.  The block `T` is in the `y`-star.  For the reverse flag, its
`A_y(S)` set consists precisely of the three `y`-star blocks with
cross-edge count two against `S`.  Hence (3) gives

```text
A_y(S)={Y_a,Y_b,T}.                              (4)
```

This is the required reverse matching.  It uses the actual cross-edge
definition, not a guessed symmetry between the two centers.

## 4. Global coefficient normalization

The canonical flag theorem uses globally fixed column representatives
`z_R` and the exact normalized relation

```text
z_leaf+2*sum_(R in A_center) z_R=0.              (5)
```

Applying (5) to (2) and (4) gives

```text
z_T+2z_Xa+2z_Xb+2z_S=0,
z_S+2z_Ya+2z_Yb+2z_T=0.                         (6)
```

Adding the two equations over `F_3` cancels `z_T` and `z_S`:

```text
2(z_Xa+z_Xb+z_Ya+z_Yb)=0.
```

Equivalently,

```text
z_Xa+z_Xb+z_Ya+z_Yb=0.                          (7)
```

This cancellation would not follow from projective supports alone.
The common global normalization in (5) is essential.

## 5. Four distinct canonical-C4 columns

The four blocks in (7) are distinct.  The two blocks at either endpoint
are distinct because `a,b` are nonadjacent.  A block from the `x` side
cannot equal one from the `y` side, because that graph triangle would
contain both nonadjacent vertices `x,y`.

They are exactly the four triangle blocks on the edges of the canonical
induced quadrilateral with opposite nonedge pairs

```text
{x,y}, {a,b}.
```

In the order

```text
(X_a,X_b,Y_a,Y_b),
```

the independently verified Wave181 centered Gram is

```text
G=
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].
```

Over `F_3`,

```text
rank(G)=3,
G(1,2,2,1)^T=0,
G(1,1,1,1)^T=(1,1,1,1)^T !=0.                  (8)
```

Any true relation among the four columns must lie in the Gram kernel.
Equation (7) is the all-equal word, so (8) rules it out.  Therefore a
forward and a reverse flag cannot share a slot of `L_x(e)`.

The two occupied slot subsets are injective and disjoint inside a
five-element set, proving (1).

## 6. Exact counting consequences

Let `U` be the selected exact-three undirected label union and let `p3`
be its number of private labels.  Every private label has selected degree
one.  Summing (1) over the nonprivate labels gives

```text
3n3
 =p3+sum_(e nonprivate) d_e
 <=p3+5(|U|-p3),
```

hence

```text
3n3+4p3<=5|U|.                                  (9)
```

Let `b` count labels with both orientations occupied and retain

```text
epsilon=sum_(occupied nonprivate orientations o)(5-m_o).
```

A bidirectional label contributes

```text
(5-m_(x->y))+(5-m_(y->x))
 =10-d_e>=5
```

to `epsilon`; every other contribution is nonnegative.  Therefore

```text
epsilon>=5b.                                    (10)
```

Also the number `T` of occupied orientations satisfies

```text
T=|U|+b.
```

## 7. Sharp current stopping point

Neither (9) nor (10) supplies a positive lower bound on `b`.  The
Wave202 aggregate/local-equality control remains compatible with `b=0`:

```text
n3=1200,
p3=3123,
234 nonprivate labels of multiplicity 2,
3 nonprivate labels of multiplicity 3,
all nonprivate labels unidirectional.
```

Then

```text
|U|=3123+237=3360,
3n3=3600,
5|U|-(3n3+4p3)=708,
epsilon=234*3+3*2=708,
b=0.
```

This is only an aggregate and local-equality arithmetic control.  It is
not a graph, code, cover, flag family, or existence claim.  It shows
precisely why the new two-center theorem, by itself, does not promote the
current conditional bound:

```text
Q>=7059 remains unchanged;
Q>=7060 is not proved.
```
