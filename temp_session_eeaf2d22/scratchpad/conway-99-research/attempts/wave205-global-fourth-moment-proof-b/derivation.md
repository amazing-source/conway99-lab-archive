# Global fourth-moment factorization and rank boundary

## 1. Frozen setting

Work over `F_3` on the conditional branch

```text
G is srg(99,14,1,2),
n3=4158, equivalently P=0,
rank_F3(D)=11.
```

Let `B` be the `99 by 231` point--triangle incidence matrix and let the
centered triangle columns be `z_T` in a nondegenerate 11-space.  Their Gram
matrix is `D`.  For a graph point `x`, write

```text
S_x=diag(B[x,*]),
P_x=-sum_(T contains x) z_T tensor z_T.
```

The inherited verification gives

```text
P_x^2=P_x,
rank(P_x)=6,
tr(P_x)=0,
sum_x P_x=0.
```

The target of this lane is

```text
h_xy=tr(P_x P_y P_x P_y),
H=(h_xy).
```

Everything below is exact over `F_3`.  No automorphism or candidate graph is
used.

## 2. The full block-pair factorization

Transferring the trace from the 11-space to the 231 coefficient labels gives

```text
h_xy
 =tr(S_x D S_y D S_x D S_y D).                    (1)
```

Equivalently, define the ordered block-pair feature

```text
u_x[(T,U)]=B[x,T]B[x,U]
```

and the symmetric crossing kernel

```text
K_D[(T,U),(R,S)]
 =D[T,R]D[R,U]D[U,S]D[S,T].                       (2)
```

Then (1) is exactly

```text
H=U K_D U^T,                                      (3)
```

where row `x` of `U` is `u_x`.

This is a genuine full-matrix identity.  It exposes, rather than eliminates,
the unknown fourth-order data: all graph dependence beyond the star-pair
incidence lies in the restriction of `K_D` to the row space of `U`.

## 3. The star-pair feature already has rank 99

The 231 graph triangles form a linear triple system: two distinct triangle
blocks share at most one graph point.  Fix a point `x` and choose two
distinct blocks `T,U` through `x`.  The `(T,U)` column of `U` is

```text
U[*,(T,U)]=e_x,
```

because no other point lies in both blocks.

Doing this once for every point exhibits all 99 unit columns.  Therefore

```text
rank_F3(U)=99.                                     (4)
```

There are

```text
99*7*6=4158
```

ordered distinct block-pair coordinates, or 2,079 unordered ones.  Each is
owned by exactly one point.  Thus neither the 99-star incidence nor the
ambient dimension of the source pair-feature space can force a rank drop in
`H`.  Any such drop must come from the special centered Gram kernel `K_D`.

The checker includes a deterministic 99-point, 231-block, 7-regular linear
triple system that reproduces (4).  Its point graph is 14-regular but is not
`srg(99,14,1,2)`; it is only a count-level control for this incidence
theorem.

## 4. Why the zero first moment does not contract the fourth moment

Put

```text
Q=B^T B.
```

Summing the pair features gives

```text
sum_x u_x=vec(Q).                                  (5)
```

Modulo three, the diagonal entries of `Q` are zero because a triangle has
three points, while a distinct intersecting triangle pair has entry one.
Thus the right side of (5) is nonzero.

At projector level, let

```text
Omega=sum_x (P_x symmetric-tensor P_x).
```

The first moment `sum_x P_x=0` does **not** imply `Omega=0`.  With the
crossing bilinear form determined by

```text
beta(A symmetric-tensor A, B symmetric-tensor B)=tr(ABAB),
```

one has

```text
h_xy=beta(P_x symmetric-tensor P_x,
          P_y symmetric-tensor P_y),

(H 1)_x=beta(P_x symmetric-tensor P_x,Omega).      (6)
```

Therefore `sum_x P_x=0` supplies no zero-row-sum theorem for `H`.

There is an equivalent superoperator formulation.  Define

```text
Phi(A)=sum_y P_y A P_y.
```

Then

```text
(H 1)_x=tr(P_x Phi(P_x)).
```

The inherited identities give `Phi(I)=0` and `tr(Phi(A))=0`, but they do not
give `Phi=0`.

## 5. Exact graph-specific row localizers

For a fixed point `x`, set

```text
M_x=D S_x D.
```

Cyclically rotating the trace in (1) and summing over `y` yields

```text
(H 1)_x
 =tr((Q o M_x)M_x),                               (7)
```

where `o` is entrywise product.  Indeed,

```text
sum_y S_y M_x S_y=Q o M_x.
```

Equation (7) identifies the missing graph-specific localizer

```text
Q o (D S_x D).
```

It can be refined to individual ordered block pairs.  Put

```text
w_TU=B(D_T o D_U).
```

Then a direct contraction gives

```text
(K_D vec(Q))[(T,U)]=w_TU^T w_TU.                  (8)
```

Thus a row-sum theorem for `H` requires the norms and mutual compatibility
of the `w_TU`, not merely `D^2=0`, `BD=0`, `sum_x P_x=0`, or the known
pairwise trace Gram.

The package checks (3), (5), (7), and (8)'s underlying contraction on an
independent seven-point exact toy incidence.  The toy is used only to replay
the algebra; no toy conclusion is transferred to the target.

## 6. Correct tensor-coordinate dimensions

The common tempting rank leap is to place `wedge^2(P_x)` in a
55-dimensional vector space.  This is false: `wedge^2(P_x)` is an
**operator** on a 55-dimensional space.

The correct ledger is

```text
V                                                11
self-adjoint End(V)                              66
trace-zero self-adjoint End(V)                   65
Sym^2(trace-zero self-adjoint End(V))          2145

wedge^2 V                                        55
self-adjoint End(wedge^2 V)                    1540
trace-zero self-adjoint End(wedge^2 V)         1539

Sym^2 V                                          66
self-adjoint End(Sym^2 V)                      2211
trace-zero self-adjoint End(Sym^2 V)           2210
```

Here

```text
tr(wedge^2 P_x)=binomial(6,2)=15=0,
tr(Sym^2 P_x)=binomial(7,2)=21=0.
```

Every correct coordinate cap is larger than 99.  It gives only the
tautological bound `rank(H)<=99`, not an endpoint obstruction.

## 7. Exact zero-first-moment hostile control

The checker constructs twelve distinct rank-six orthogonal projectors in the
nonsquare 11-space with form

```text
diag(1,1,1,1,1,1,1,1,1,1,2).
```

Six are coordinate projectors and six are their conjugates by one exact
orthogonal reflection.  Each projector:

- is self-adjoint and idempotent;
- has rank six and trace zero;
- has star-space discriminant one; and
- is generated by seven singular columns with Gram `J_7-I_7`, zero column
  sum, and `P=-sum(z tensor z)`.

The twelve projectors sum to zero.  Adding 29 triples of one projector gives
exactly 99 labelled projectors and preserves the zero sum.  The resulting
control has

```text
rank(pair-trace Gram)=8,
pair-trace Gram times 1=0,

rank(H)=9,
H-row-sum distribution 0^6 1^91 2^2,
740 ordered entries with g_xy != h_xy,
302 nonzero coordinates in Omega.
```

This exactly refutes the generic implication

```text
sum_x P_x=0  =>  H 1=0.
```

The control does not glue its local simplexes into 231 projectively distinct
columns, repeats 87 projector labels, has no degree-three point--triangle
incidence, and is not a graph or endpoint realization.  It cannot refute an
identity using those missing premises.

## 8. Dormant equality-face consequence

One candidate considered during the wave was the unproved assertion

```text
tr(P_xP_y)=2 for every graph nonedge.
```

If a future graph-specific theorem established it, the complete pair-trace
Gram would be

```text
G_P=2(J-I-A)=A+I-J=E,
```

the rank-54 idempotent from the point module.  In the nondegenerate
65-dimensional trace-zero self-adjoint space, the span rank `r` of the 99
projectors would then satisfy

```text
54<=r<=59,
dim ker(point-to-projector map)>=40.
```

Since the known incidence dependency code has dimension at most 33, this
would force at least seven additional global projector relations beyond the
incidence dependencies.  It would be a useful new module target, not yet a
contradiction.

This equality face is not promoted here.  A parallel exploratory lane
reported rank-nine `t=6` radical lifts, but that report is not an input or a
verified claim of this package.  In any event the necessary uniform-nonedge
premise has not been proved, so no conclusion in this lane uses it.

## 9. Boundary and next exact theorem

This lane derives a full-matrix factorization and a sharp obstruction to the
naive globalization route:

```text
the star-pair feature has full rank 99,
the correct tensor spaces are larger than 99,
and sum_x P_x=0 does not force a fourth-moment contraction.
```

Therefore the fourth-order route can advance only by proving new
graph-specific information about one of the equivalent objects

```text
K_D restricted to row(U),
Q o (D S_x D),
w_TU=B(D_T o D_U),
Phi(A)=sum_y P_y A P_y.
```

A particularly concrete next theorem is to classify the norms
`w_TU^T w_TU` for two distinct triangle blocks through a common graph point
and then sum the resulting values over each seven-block star.

No rank-11 exclusion, endpoint exclusion, strict `n3` improvement, graph
construction, or Conway-99 resolution follows.
