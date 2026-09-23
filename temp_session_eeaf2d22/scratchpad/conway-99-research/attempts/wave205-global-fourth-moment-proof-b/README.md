# Wave 205 proof B: global fourth-moment boundary

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

For the conditional prism-free rank-11 endpoint, this package derives the
exact full-matrix identity

```text
H=U K_D U^T,
```

where `U` is the ordered point-star triangle-pair feature and `K_D` is the
crossing four-Gram kernel.  The key obstruction is

```text
rank_F3(U)=99.
```

Thus star incidence and ambient tensor dimensions cannot themselves force a
rank drop in `H`.  The package also derives

```text
(H 1)_x=tr((Q o (D S_x D))(D S_x D)),
Q=B^T B,
```

and gives a 99-projector scoped control showing that `sum_x P_x=0` does not
imply `H 1=0`.

The newly exposed graph-specific invariant is the restriction of `K_D` to
the full-rank star-pair subspace, equivalently the localizers
`Q o (D S_x D)` or the vectors `w_TU=B(D_T o D_U)`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave205-global-fourth-moment-proof-b\exact_check.py --verify attempts\wave205-global-fourth-moment-proof-b\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave205-global-fourth-moment-proof-b\test_exact_check.py
```

No rank-11 or endpoint exclusion follows.
