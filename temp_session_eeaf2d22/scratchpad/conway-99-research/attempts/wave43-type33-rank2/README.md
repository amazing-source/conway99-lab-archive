# Wave 43 type-`3+3` rank-two obstruction

Status: **DERIVED, pending independent verification**. The endpoint and
Conway-99 remain **UNKNOWN**.

This package closes the one-edge local rank-27 mechanism left open by the
even-type Wave 43 lane. Conditional on the prism-free endpoint, the local
type `3+3` has:

```text
rank_F7(K39) = 25 + rank_F7(D),
```

because its Wave 42 border term `F` is identically zero. The already verified
rank-27 floor rules out residual ranks zero and one. Thus equality at 27
would require `rank(D)=2`.

## Complete pivot/mate CSP

Over a field of odd characteristic, every rank-two symmetric matrix has an
invertible principal `2 x 2` submatrix. The checker enumerates:

1. all 66 pivot-coordinate pairs;
2. all deranged, distinct images of the two pivot coordinates;
3. whether the pivot coordinates are matched together in `R`, or their two
   distinct mates if they are not; and
4. every remaining deranged all-different border assignment.

For an invertible pivot `P`, rank two is equivalent to a zero Schur
complement:

```text
D_ij = D_iP (D_PP)^(-1) D_Pj.
```

The diagonal instances give exact unary domains. Each off-diagonal instance
then determines the required `W_R(i,j)` value. It must be `1` (not mates) or
`6=-1 mod 7` (mates); every other value is impossible. Backtracking enforces
that the forced mate edges form one perfect matching.

No completed-graph automorphism is imposed.

## Result

```text
all branches:                   666,666
invertible-pivot branches:      491,220
branches surviving unary cuts:  60,306
backtracking nodes:             122,922
complete leaves:                      0
```

Hence no endpoint type-`3+3` local rank-two residual exists, subject to
independent verification.

Combined with the separate even-type candidate theorem, this would give the
scoped endpoint consequence

```text
n3=4158  ==>  every edge-local K39 has rank_F7 at least 28
           ==> rank_F7(M) >= 28.
```

That rank bound is still compatible with the known global ceiling 44, so it
does not exclude the endpoint.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-type33-rank2\exact_check.py `
  --verify attempts\wave43-type33-rank2\exact-results.json
```
