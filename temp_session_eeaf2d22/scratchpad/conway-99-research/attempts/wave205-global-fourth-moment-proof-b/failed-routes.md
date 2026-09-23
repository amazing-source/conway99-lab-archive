# Failed and blocked routes

## Treating `wedge^2(P_x)` as a 55-coordinate vector

`wedge^2(P_x)` is an operator on the 55-dimensional space `wedge^2 V`.
Its self-adjoint operator-coordinate space has dimension 1,540, or 1,539
after imposing trace zero.  The analogous symmetric-square dimensions are
2,211 and 2,210.  None gives a rank bound below 99.

## Using the 65-dimensional projector space directly

The pair trace `tr(P_xP_y)` is bilinear in the 65-dimensional trace-zero
self-adjoint space.  The fourth trace is quadratic in each projector.  Its
natural quadratic feature space has dimension

```text
dim Sym^2(F_3^65)=2145,
```

so the pair-trace rank cap does not transfer to `H`.

## Inferring `H 1=0` from `sum_x P_x=0`

The implication is false even for 99 rank-six trace-zero self-adjoint
idempotents in a nonsquare 11-space, each with the exact local seven-column
simplex.  The package's scoped control has zero first moment but nonzero
quadratic moment and fourth-row-sum distribution `0^6 1^91 2^2`.

The control is not an endpoint realization; it refutes only the generic
projector implication.

## Seeking rank loss from point-star pair incidence

The ordered pair feature

```text
u_x[(T,U)]=B[x,T]B[x,U]
```

has rank exactly 99.  For each point `x`, any two distinct triangle blocks
through `x` supply a feature column equal to `e_x`.  Thus incidence before
the centered four-Gram contraction has no rank deficiency to exploit.

## Replacing the second moment by the first

The exact identities are

```text
sum_x P_x=0,
sum_x u_x=vec(B^T B),
Omega=sum_x(P_x symmetric-tensor P_x).
```

The second and third expressions need not vanish.  Any proof that silently
replaces them by zero drops the unique-intersection contribution of two
distinct blocks through one graph point.

## Ordinary association-algebra closure

The SRG matrices lie in `span{I,A,J}`, but no proof shows that `H` lies in
this three-dimensional algebra.  Wave 204 determines `h_xy` on graph edges
only, and the nonedge values may vary.  Association-algebra eigenvalue or
characteristic-polynomial calculations are therefore conditional until a
nonedge constancy theorem is proved.

## Uniform nonedge pair trace

The attractive candidate `tr(P_xP_y)=2` for every nonedge would make the
pair-trace Gram the rank-54 idempotent `A+I-J` and force at least seven
projector relations beyond the known incidence dependency code.

The required local lower bound is not sealed.  A parallel exploratory lane
reported rank-nine nonedge cross-Gram `t=6` radical lifts, but this package
does not independently verify or rely on that report.  It records the
conditional consequence only and does not use or promote uniformity.

## Final boundary

The proposed route is blocked precisely at the graph-specific second-moment
objects

```text
K_D restricted to row(U),
Q o (D S_x D),
w_TU=B(D_T o D_U),
Phi(A)=sum_y P_y A P_y.
```

No solver nonhit, relaxed control, or ambient dimension count proves these
objects incompatible with the endpoint.
