# Retained failed runs

## Hostile-route parameterization

The first invocation of `exact_check.py` stopped before producing a result:

```text
CheckError: e2 endpoint bound is not 1122
```

The endpoint-specific Maclaurin checker was being reused deliberately with
the hostile value `tr(B^2)=54`, which should produce `e2=1125` and the old
determinant cap 45.  The function was split into a general exact computation
plus an optional endpoint-value gate.  The endpoint path still requires
`e2=1122`, `e2/C(44,2)=51/43`, and cap 42; only the hostile relaxation calls
the ungated arithmetic path.  The corrected run and all 25 tests pass.

No solver, floating-point calculation, or candidate Wave-23 artifact was
used.

## Verifier correction of one hostile control

The frozen discovery commit
`b3763368049422b5f10f949a8ac02b14ec0fb54f` claimed that
`(h,det(Q),det(B))=(9,3,27)` survived after omitting the `det(Q)` residue
and signature package.  The independent audit committed at
`a6771108ec00bddfcc8ae5b41779760673fef22e` correctly observed that this
triple violates the still-frozen consequence `det(B)=1 mod 4`, since
`27=3 mod 4`.

The invalid control is retained here rather than silently rewritten.  It is
replaced in the executable hostile ledger by the single-relaxation control
`(9,1,9)`: omit only the signature obstruction `det(Q)!=1`, while retaining
`det(Q)=1 mod 4`, `h=1 mod 4`, `det(B)=1 mod 4`, smoothness, factorization,
and the determinant cap.  The main endpoint proof never used the invalid
control and is unchanged.
