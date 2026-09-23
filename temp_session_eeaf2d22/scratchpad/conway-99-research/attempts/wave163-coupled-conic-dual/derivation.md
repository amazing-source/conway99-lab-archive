# Derivation

## 1. Why scalar cuts loop

Each retained inequality has the form

```text
v^T B_tau(x) v >= 0.
```

Wave159 gives an exact rational point satisfying all fifteen selected scalar
inequalities, while the complete root-3 and root-12 matrices still have new
negative directions.  Wave162 then shows:

- none of the three active Wave159 functionals is zero on the common stored
  affine slice;
- the newest negative direction at each persistent root is independent of
  the active-direction span.

Thus the active scalar equalities do not expose a forced PSD face, and the
new violations are not repetitions of their kernels.

## 2. Compressed whole-block multipliers

Collect exact rational directions as the columns of `U_tau`.  Restrict the
dual PSD multiplier to

```text
Z_tau = U_tau Y_tau U_tau^T,  Y_tau >= 0.
```

Then

```text
<Z_tau,B_tau(x)>
  = <Y_tau, U_tau^T B_tau(x) U_tau>.
```

Define the small compressed pencil

```text
C_tau(x) = U_tau^T B_tau(x) U_tau.
```

The diagonal entries of `C_tau` are the old scalar cuts.  Its off-diagonal
entries are bilinear flag moments between different stored directions.
They are the first information in this lane that cannot be represented as
an independently chosen list of rank-one inequalities.

With six root-3 and eight root-12 directions, the two symmetric `Y` matrices
have 21 and 36 coordinates, respectively.

## 3. Quotient-row test

Flatten the upper triangles of `C_3(x)` and `C_12(x)`.  Each of the 57
entries is an exact affine coefficient row on

```text
(1,x7[208],x8[916]).
```

Let `R` be the row space of the universal endpoint equalities, with constants
included in the same augmented coordinate system.  Compute the quotient map

```text
span(compressed rows) -> augmented coefficient space / R.
```

If this map has rank 57, no nonzero symmetric pair `(Y3,Y12)`, even an
indefinite one, produces an affine identity in this compressed lane.  This
is a rigorous scoped null result once reconstructed over the rationals.

If a kernel survives, recover it exactly.  Only kernel elements with
`Y3,Y12` positive semidefinite can be conic exposing multipliers.

## 4. Constant and slack checks

Coefficient cancellation alone is not a certificate.  The augmented
constant must have the correct exact sign.

An infeasibility dual may also use the nonnegativity constraints on count
variables.  Algebraically this adds a coordinatewise nonnegative slack row
to the cancellation equation.  The quotient-rank test without those slacks
does not exclude such a Farkas certificate; that cone-membership problem is
a separate required step.

Likewise, a certificate on the fixed-`x7`/pair-root-zero reconstruction slice
does not lift automatically to the full endpoint.  The two affine systems
must never share a verdict.

## 5. Completion criterion

This lane advances the target only if it yields one of:

1. an exact full-endpoint infeasibility identity with PSD multipliers and
   correct nonnegative slacks;
2. an exact full-endpoint exposing identity that reduces a covariance cone,
   followed by a valid reduced problem;
3. a rigorously scoped rank/cone null result that excludes the entire stated
   compressed multiplier family.

No numerical solver status, approximate eigenvalue, or fixed-slice identity
meets that criterion.

