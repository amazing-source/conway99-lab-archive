# Wave 97: characteristic-seven exterior and matroid shift

Status: `DERIVED` discovery; independent verification is required.

This package moves the conditional Conway-99 endpoint into three exact
spaces without assuming a graph automorphism:

1. the Schur evaluation algebra of the Seidel hull;
2. the second compound matrix \(E=C_2(S)\), indexed by the 4,851 unordered
   vertex pairs; and
3. the finite orthogonal embedding
   \(O^-(16,7)\subset O^-(42,7)\).

It finds new exact structure but no contradiction. Rank 28, a strict upper
bound below 4,158, Conway-99, and novelty all remain `UNKNOWN`.

## Exact outcome

Let
\[
S=2A-J+I,\qquad R=\operatorname{row}_{\mathbf F_7}(S).
\]
At the difficult row, \(\dim R=28\), the verified Wave 80 code has
\[
C/R\cong O^-(16,7),\qquad d(R^\perp)\ge6.
\]

The Schur algebra closes in three steps:
\[
\boxed{R*R=\mathbf1^\perp,\qquad R*R*R=\mathbf F_7^{99}.}
\]
Wave 51 already supplied the pure-square rank behind the first equality.
Wave 97 records the equality as a code product, proves the full cube, and
identifies the corresponding degree-\(0,1,2,3\) Hilbert function
\[
(1,28,98,99).
\]
The 99 quadratic Veronese images form a circuit: their unique dependence
has all 99 coefficients nonzero.

For the second compound
\[
E=C_2(S),\qquad E_{\{a,b\},\{c,d\}}
  =\det S[\{a,b\},\{c,d\}],
\]
one obtains, modulo seven, a projective self-orthogonal code
\[
\boxed{\operatorname{row}_{\mathbf F_7}(E)
       \text{ has parameters }[4851,378]_7.}
\]
Every distinguished row has weight 1,947. The complete conditional Smith
form at rank 28 is
\[
\boxed{
\operatorname{SNF}(E)=
\operatorname{diag}\left(
1^{378},7^{1204},49^{1687},343^{1204},
2401^{280},24010^{98}\right).
}
\]
The package gives the analogous formula for all eight surviving even ranks
\(28,30,\ldots,42\).

Finally, Witt extension makes all nondegenerate
\(O^-(16,7)\) subspaces with \(O^+(26,7)\) complement one
\(O^-(42,7)\)-orbit. Norm-16 and norm-18 short classes both lie in the same
square-anisotropic projective orbit. Thus the abstract orthogonal space
cannot distinguish those two lattice alternatives; coordinate weights must
be retained.

## Reproduce

```powershell
python -B attempts/wave97-f7-exterior-matroid/exact_check.py `
  --verify attempts/wave97-f7-exterior-matroid/exact-results.json

python -B -m unittest discover `
  -s attempts/wave97-f7-exterior-matroid -p "test_*.py" -v
```

The checker uses only exact standard-library arithmetic. It never
materializes the 4,851 by 4,851 compound matrix.

## Files

- `protocol.md`: frozen imports, target, and status rules.
- `derivation.md`: proofs of the Schur, compound, Smith, and orbit formulas.
- `exact_check.py`: deterministic exact arithmetic.
- `exact-results.json`: canonical machine-readable output.
- `test_exact_check.py`: 14 regression and hostile-control tests.
- `failed-routes.md`: exact null boundary and next useful attacks.
- `verifier-request.md`: separated independent-verification assignment.
- `input-freeze.sha256`: byte hashes of imported packages.
- `run-report.yaml`: AGENTS-schema discovery report.
- `package-manifest.sha256`: package integrity seal.

Nothing in this discovery package is labelled `VERIFIED`.
