# Derivation

## 1. Affine covariance pencils

For root type `tau`, let

```text
B_tau(x) = R_tau M_tau(x) - s_tau s_tau^T.
```

At the frozen endpoint, `M_tau(x)` is linear in the order-seven and
order-eight induced counts and `s_tau` is fixed by the order-six counts.
Hence `B_tau(x)` is an affine symmetric-matrix-valued function of `x`.

Every graph-compatible count vector must satisfy

```text
B_tau(x) >= 0.
```

For an integer flag direction `v`, this implies the scalar linear inequality

```text
L_v(x) = v^T B_tau(x) v >= 0.
```

The fifteen stored cuts are primitive integer rescalings of such
functionals.

## 2. Exact affine non-forcing certificates

Let `A x = b` denote the common equality system frozen by the Wave150 model,
the Wave44 row system, deletion, marked rows, the pair-root zero face, and
the common fixed order-seven vector. If `L_v` were forced to zero by these
equalities, then `L_v(x_1)=L_v(x_2)=0` for every two stored exact solutions
of the common system.

Wave162 evaluates `L_v` directly with `Fraction` arithmetic. For each of the
three Wave159 active directions it records:

```text
L_v(x_15) = 0,
L_v(x_j) != 0
```

for another stored fixed-slice witness `x_j`. Equivalently, the exact
homogeneous difference `d=x_j-x_15` satisfies the common stored equality
system and

```text
L_v(d) != 0.
```

This is a primal row-space non-membership certificate. It rules out an
affine-forced zero. It does not rule out the possibility that adding the
whole PSD cone forces a face by a more subtle conic dual identity.

## 3. PSD zero rigidity

If `B>=0`, write `B=C^T C`. Then

```text
v^T B v = ||Cv||^2.
```

Therefore `v^T B v=0` implies `Cv=0`, and hence `Bv=0`. For an indefinite
matrix the implication is false in general.

If `r` independent directions are known to lie in the kernel of every
feasible `d`-by-`d` PSD matrix, an exact change of basis places the matrix
in a face isomorphic to

```text
S_+^(d-r).
```

The Wave159 active directions have exact ranks one for root 3 and two for
root 12. These ranks are certified by nonzero integer minors stored in
`facial-reduction-audit.json`.

## 4. Escape directions

The fifteen-cut witness is still separated by new exact negative directions
at roots 3 and 12. Wave162 appends each new direction to the Wave159 active
directions for that root and computes an exact nonzero determinant minor.
The ranks rise:

```text
root 3:  1 -> 2,
root 12: 2 -> 3.
```

Thus neither new separator lies in the span of the active directions. This
is an exact explanation of why the three conditional kernel directions do
not close the persistent blocks.

## 5. Dual exposing identity

A genuine facial reduction needs a certificate using the cone, not only the
affine hull. A PSD multiplier `Z_tau` satisfies

```text
<Z_tau, B_tau(x)> >= 0
```

for every PSD-feasible `B_tau(x)`. If exact multipliers give an identity

```text
sum_tau <Z_tau, B_tau(x)> + lambda^T(Ax-b) = 0,
```

then the affine term vanishes on feasible points and the nonnegative trace
terms must vanish. For PSD matrices, `<Z,B>=0` implies that the range of `Z`
lies in the kernel of `B`. The ranges of the `Z_tau` therefore expose forced
faces.

No such exact `Z_tau,lambda` was found in the accessible data. The stored
active cuts are rank-one choices `Z=vv^T`, but their coefficients are not
forced to vanish by the common affine system, and their zeros at the final
witness were imposed during reconstruction.
