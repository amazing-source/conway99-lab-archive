# Wave 102 verification

Verdict: `VERIFIED_WITH_CORRECTIONS`.

Verified:

```text
7*N14 <= 55440-5*n3-O/2
N14 <= 2*floor((55440-5*n3-O/2)/14)
f mod 2 = B D 1
B B^T = I+A over F2
rank_2(A)=54
rank_2(I+A)=45
```

The verifier strengthens the small-prism conclusion to `P=3 => O>=4` and
narrows nonzero `ker(B^T)` check weights to the necessary candidates
`36,40,44,48,52,56,60`.

The `3 by 3` rook graph and `C4 square K3` pass the stated local checks, but
neither is certified to extend to 99 vertices.  No strict `n3` upper bound,
graph exclusion, construction, or Conway-99 resolution follows.

Reproduce:

```powershell
python -B verification\wave102-prism-incidence-code\independent_verify.py
python -B -m unittest discover `
  -s verification\wave102-prism-incidence-code -p "test_*.py" -v
python -B attempts\wave102-prism-incidence-code\exact_check.py --verify
python -B -m unittest discover `
  -s attempts\wave102-prism-incidence-code -p "test_*.py" -v
```
