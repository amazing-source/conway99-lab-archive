# Wave 109: local characteristic-seven projector

Status: `DERIVED`; independent verification required.

Conditional on a hypothetical `srg(99,14,1,2)` containing the Wave 105
induced `C4` Cartesian `K3` motif, its forced incidence matrix `P` gives

```text
Q=[one P]                    rank 13, primitive,
Lambda=ker_Z(Q^T)            rank 74,
det(Lambda)=det(Q^T Q)=2^22 3^10 5^2.
```

The determinant is nonzero modulo seven. Its square class shows that
`Lambda/7Lambda` is the **non-split** space `O^-(74,7)`, of Witt index 36;
calling it split would reverse the determinant criterion in odd
half-dimension.

If `D` is the unknown 87-vertex outside adjacency matrix, then `D` preserves
`Lambda`. On this lattice,

```text
B=D+4I,          B^2=7B,
rank_Q(B)=42,    nullity_Q(B)=32.
```

Modulo seven, `im(B)` is totally isotropic. If
`r=rank_F7(2A-J+I)`, an exact Schur complement proves

```text
rank_F7(B|Lambda)=r-12.
```

Thus the eight imported global rows `r=28,30,...,42` become local ranks
`16,18,...,30`. All are at most 36, so this orthogonal-space test excludes
none of them. The package also records the resulting conditional Smith and
index formulas. The motif extension, Conway-99, and literature novelty
remain `UNKNOWN`.

Reproduce with the standard Python library:

```powershell
python -B attempts\wave109-c4boxk3-local-projector\exact_check.py `
  --output attempts\wave109-c4boxk3-local-projector\exact-results.json `
  --verify
python -B -m unittest discover `
  -s attempts\wave109-c4boxk3-local-projector -p "test_*.py" -v
```
