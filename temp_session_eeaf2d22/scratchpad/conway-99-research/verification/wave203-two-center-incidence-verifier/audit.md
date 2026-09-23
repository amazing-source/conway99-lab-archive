# Independent Wave203 two-center incidence audit

## Verdict

`VERIFIED_TWO_CENTER_CAPACITY_NO_BOUND_PROMOTION`.

Conditionally on the frozen prism-free rank-11 endpoint, every selected
exact-three nonedge label `e={x,y}` satisfies

```text
m_(x->y)+m_(y->x)<=5.                            (1)
```

The same slot proof applies to the full canonical exact-three flag pool;
the selected statement is its immediate subset consequence.

This is a genuine two-center theorem, but it does not improve the current
conditional numerical bound:

```text
Q>=7059 remains unchanged;
Q>=7060 is not proved.
```

## 1. Shared five-slot geometry

Let `a,b` be the two common neighbors of the nonedge `xy`.  The blocks
through `xa,xb` are distinct members `X_a,X_b` of the seven-block
`x`-star.  The other five `x`-star blocks form `C_x(y)` and are
anticomplete to `y`.  Symmetrically, the five `y`-star blocks outside
`Y_a,Y_b` form `C_y(x)`.

For an `x->y` flag `(x,T)`,

```text
A_x(T)={X_a,X_b,S}
```

with a unique `S in C_x(y)`.  Equal choices of `S` give equal `A_x`
sets, so verified fixed-center injectivity makes `T->S` a partial
injection.  A reverse `y->x` flag uses its leaf triangle `S` as a slot
in the same set `C_x(y)`.  Thus both directions inject into one set of
five slots; no surjectivity onto all five candidates is assumed.

## 2. Matched reverse occupancy is impossible

If a forward flag has third block `S`, then by definition

```text
j(S,T)=2.
```

If a reverse flag has leaf `S`, the fixed type of its leaf `x` gives the
two blocks `Y_a,Y_b`, and `j(S,T)=2` forces

```text
A_y(S)={Y_a,Y_b,T}.
```

Using the globally fixed columns and the canonical leaf coefficient one,
the two relations are

```text
z_T+2(z_Xa+z_Xb+z_S)=0,
z_S+2(z_Ya+z_Yb+z_T)=0.
```

Their sum cancels `T,S` and forces the all-equal relation

```text
z_Xa+z_Xb+z_Ya+z_Yb=0.                          (2)
```

The four columns are distinct: `a,b` are nonadjacent, so each endpoint
uses two different local blocks, and no graph triangle can contain both
nonadjacent centers `x,y`.  They are the four canonical quadrilateral
columns.  In their grid order Wave181 gives

```text
G=
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].
```

Over `F_3`, `G` has rank three and checkerboard kernel
`<(1,2,2,1)>`, while

```text
G(1,1,1,1)^T=(1,1,1,1)^T.
```

Thus (2) is impossible.  The two directional slot sets are disjoint
subsets of five slots, proving (1).

## 3. Exact global consequences

Let `U` be the selected exact-three undirected label union.  Each private
label counted by `p3` has selected degree one; every other label has
combined degree at most five by (1).  Hence

```text
3n3<=p3+5(|U|-p3),
3n3+4p3<=5|U|.                                  (3)
```

Let `b` count nonprivate labels with both orientations occupied.  Such a
label contributes

```text
(5-m_(x->y))+(5-m_(y->x))
 =10-(m_(x->y)+m_(y->x))>=5
```

to the Wave198 orientation deficit.  Therefore

```text
epsilon>=5b.                                    (4)
```

## 4. Why the bound does not move

No frozen row forces `b>0`.  The Wave202 aggregate/local-equality control
can keep every nonprivate label unidirectional:

```text
n3=1200,
p3=3123,
234 nonprivate labels of multiplicity 2,
3 nonprivate labels of multiplicity 3,
b=0.
```

It has

```text
|U|=3360,
3n3=3600,
5|U|-(3n3+4p3)=708,
epsilon=708.
```

This is an arithmetic and local-equality control only, not a graph, code,
cover, flag family, or existence claim.  It proves only that the current
linear and one-/two-center rows do not exclude `b=0`.

## 5. Source comparison and integrity

The source-blind result was frozen before either Wave203 source was
opened:

```text
independent freeze:
43721bc8b667209600dea1aff80a5b930f03b63d02062eb69ff7adf8abe3e2d1
```

After the freeze:

```text
independent replay/tests:  PASS / 11 of 11
primary replay/tests:      PASS / 7 of 7
hostile replay/tests:      PASS / 7 of 7
comparison tests:          5 of 5 PASS
```

The primary and hostile source manifests match their sealed hashes.
No mathematical discrepancy or repair was found.

No graph, code, cover, flag-family, SAT, LP, configuration,
enumeration, isomorphism, or brute-force search was used.  Rank 11,
endpoint existence, Conway-99, and external novelty remain `UNKNOWN`.
