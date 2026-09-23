# Wave 48 exact facial-reduction verification protocol

## Scope and evidence boundary

This verifier checks only two exact claims:

1. the frozen Wave44 integer row system has rational rank 93 and affine
   nullity 116 in its 209 variables; and
2. each of the three frozen Wave45 and eight frozen Wave47 moment families has
   the claimed complete universal kernel on that rational affine space.

No Wave48 discovery implementation may be imported or executed. The discovery
`exact-faces.json` remains unopened until the independent reconstruction has
been written and hashed. Floating solver result files are never opened and
have no evidentiary role. Feasibility, endpoint `n3=4158`, graph construction,
and every strict upper bound remain `UNKNOWN` or `NOT_PROVED`.

## Independent exact method

Concatenate the Wave44 `base`, `vertex`, `edge`, and `nonedge` row families in
that order to form the integer system `A X=b` with 170 rows and 209 columns.
Compute a fraction-free rational RREF of `[A|b]`. Record its pivot columns,
rank, consistency, one rational particular solution, and a rational nullspace
basis. Verify all identities by exact integer arithmetic after clearing
denominators. The affine nullity is `209-rank`.

For each frozen moment family, reconstruct

```text
M(X) = C + sum_{j=0}^{207} X_j M_j
```

directly from its sparse exact class coefficients and the frozen lower-order
counts. Normalization by a positive scalar is irrelevant to kernels.

For a particular point `X0` and nullspace columns `N_t`, build the exact
vertical stack

```text
S = [ M(X0) ; M(N_1) ; ... ; M(N_116) ].
```

The universal kernel is exactly `ker(S)`: inclusion follows by substitution;
completeness follows because every affine point is `X0+sum_t u_t N_t`.
Compute a primitive integer basis for `ker(S)`, check every vector against
every constant/direction matrix exactly, and certify completeness by the exact
rank identity

```text
rank(S) + dim ker(S) = matrix_size.
```

Independently record modular ranks over at least three primes as secondary
cross-checks. Only after sealing this reconstruction may the verifier open
`exact-faces.json` and compare family names, bases (as subspaces), ranks,
nullities, forced-zero coordinates, and exact affine-kernel identities.

## Labels

- `VERIFIED_SCOPED`: every exact reconstruction and comparison passes.
- `REFUTED`: an exact mismatch is exhibited.
- `UNKNOWN`: reconstruction or comparison is incomplete.

Discovery does not certify itself. A solver status, residual, eigenvalue, or
floating dual cannot change these labels.
