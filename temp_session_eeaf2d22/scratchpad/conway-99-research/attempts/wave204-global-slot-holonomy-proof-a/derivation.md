# Derivation

## 1. Frozen conditional setting

Assume the prism-free endpoint and ternary rank-11 branch:

```text
n3=4158, P=0, rank_F3(D)=11.
```

The Wave 203 arithmetic/local-interface control permits `b=0`, where no
selected nonprivate exact-three label uses both endpoint orientations.  That
control is not an asserted flag family or endpoint object.

For a selected flag with oriented nonedge label `x->y`, let `a,b` be the two
common neighbors of `x,y`.  Let `X_a,X_b` be the corresponding two blocks in
the `x`-star, let `T` be the leaf block in the `y`-star, and let `S` be the
unique third `x`-star block in `A_x(T)`.  The verified global normalization is

```text
z_T+2(z_Xa+z_Xb+z_S)=0.
```

Over `F_3`, this is

```text
z_T=z_S+z_Xa+z_Xb.                              (1)
```

## 2. The smallest honest transition object

Let `Gamma` have the 231 triangle blocks as vertices.  Every existing selected
flag gives one directed edge

```text
S -> T
```

with gain

```text
g(S->T)=z_T-z_S=z_Xa+z_Xb.                      (2)
```

This is the smallest honest gain graph supplied by the frozen relations.
There is no forced 2-cell:

- Wave 203 gives only a partial injection for one oriented nonedge;
- the canonical quadrilateral Gram has kernel
  `<(1,2,2,1)>`, but a Gram-kernel word is only a necessary location for a
  true dependence;
- the frozen branch does not assert a checkerboard circuit on every canonical
  quadrilateral.

Thus the honest incidence object is one-dimensional unless additional true
relations are supplied.

## 3. Definitional coboundary theorem

The potential on a block vertex `R` is its globally fixed column `z_R`.
Equation (2) says exactly

```text
g=d z.
```

For any genuine directed block cycle

```text
S_0 -> S_1 -> ... -> S_(k-1) -> S_0,
```

one has

```text
sum_i g(S_i->S_(i+1))
 =sum_i (z_(S_(i+1))-z_(S_i))
 =0.                                             (3)
```

The exact checker instantiates (3) for `k=3,4,5`.  This is a definitional
theorem, not an endpoint obstruction: the holonomy vanishes because the gain
was already a global coboundary.

## 4. Why a center walk does not compose

Consider consecutive oriented labels

```text
x->y, y->z.
```

The first flag gives a block arrow

```text
S_xy -> T_xy,
```

where `T_xy` belongs to the `y`-star.  The second gives

```text
S_yz -> T_yz,
```

where `S_yz` also belongs to the `y`-star.  These arrows compose only if

```text
T_xy=S_yz                                         (4)
```

as actual triangle blocks.  Being in the same seven-block star does not imply
(4).  Wave 203 proves neither (4), a total map on five slots, surjectivity, nor
a cross-label chart identification.

For a projected center cycle with flags indexed cyclically, its gain sum is

```text
sum_i (z_(T_i)-z_(S_i))
 =sum_i (z_(T_(i-1))-z_(S_i)),                   (5)
```

where the second expression groups the incoming and outgoing slot at each
center.  The right side is a **slot-mismatch defect**.  It is not holonomy
unless every incoming block equals the next outgoing block.

The assumption `b=0` only removes opposite orientations of the same selected
nonedge.  It supplies no equality in (4) for different labels.

## 5. Exact rank-11 local controls

The checker uses

```text
H=diag(1,1,1,1,1,1,1,1,1,1,2)
```

over `F_3`.  Its determinant is the nonsquare `2`.

For each `k in {3,4,5}`, the machine-readable control contains `k` displayed
point-stars

```text
Z_i=(z_(i,0),...,z_(i,6)).
```

They satisfy exactly

```text
<z_(i,r),z_(i,s)>=0 if r=s, and 1 otherwise,
sum_r z_(i,r)=0.
```

Thus every displayed star is the local projective singular `A6` simplex.
The cyclic flag relation is

```text
z_((i+1),0)=z_(i,1)+z_(i,2)+z_(i,3).            (6)
```

Interpret `z_(i,1)` as `S_i`, `z_(i,2),z_(i,3)` as `X_a,X_b`, and
`z_((i+1),0)` as `T_i`.  Equation (6) is exactly (1).

All displayed columns are singular and projectively distinct.  Singular
fillers raise their span to rank 11 without altering the local equations.
Only the forward cyclic orientations are present, so the displayed labels
have `b=0`.

At every center,

```text
incoming block = z_(i,0),
outgoing block = z_(i,1),
```

and these are different.  Hence none of the consecutive block arrows
composes.  The exact projected defects are:

```text
k=3: (0,0,0,0,0,1,1,1,0,1,2)
k=4: (0,0,1,1,1,1,1,2,1,0,2)
k=5: (0,1,1,2,1,1,1,2,1,0,1).
```

All are nonzero.  Therefore the implication

```text
rank-11 local A6 stars + normalized flag equations + b=0
  => a center-cycle cocycle
```

is refuted by exact relaxed controls.

## 6. Independent five-slot extension ambiguity

Wave 203 supplies partial injections, not elements of `S_5`.  The checker
freezes the same one-point interface on every edge,

```text
0 -> 0.
```

It then gives two full extensions:

```text
all identity maps,
one extension swapping unused slots 1 and 2 and all others identity.
```

Both agree on every supplied partial value.  Their full permutation
monodromies are respectively the identity and `(1 2)`.  Thus even after one
chooses to add total maps, their monodromy is not an invariant of the Wave
203 interface.

## 7. Exact premise ledger

The orthogonal controls satisfy:

- exact `F_3` arithmetic;
- the correct nonsquare nondegenerate 11-dimensional form;
- projectively distinct singular displayed columns;
- exact seven-column `A6` stars;
- exact normalized flag relations;
- directed center cycles of lengths 3, 4, and 5; and
- `b=0` on the displayed labels.

They do **not** satisfy or assert:

- 99 point-stars;
- 231 global columns;
- the global self-orthogonal frame sum;
- a point-triangle incidence matrix;
- SRG adjacency and common-neighbor axioms;
- Wave 201 or Wave 202 cover totals; or
- an endpoint code or Conway-99 graph.

Accordingly they refute only the claimed implication from the listed local
premises.  They are not counterexamples to the existence or nonexistence of
the Conway graph.

## Boundary

The exact block gain is a tautological coboundary, while center-cycle and
five-slot permutation holonomy are not defined by the frozen interface.
A useful next step must first force actual block matching, a total
star-to-star transition, or a global higher-incidence relation.

No rank-11 exclusion, endpoint exclusion, `Q>=7060`, strict `n3` improvement,
graph, code, or Conway-99 resolution follows.
