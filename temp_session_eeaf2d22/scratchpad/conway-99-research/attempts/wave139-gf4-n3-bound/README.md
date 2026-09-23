# Wave139: three-class GF(4) graph-state checkpoint

Claim label: `DERIVED` for the invariant-space dimension; `UNKNOWN` for
coefficient optimization and every realization claim.

The verified self-dual additive GF(4) graph-state enumerator has 5,050 raw
three-class states `(nI,nY,nR)`. Odd `nY` vanishes, leaving 2,550 variables.

The normalized MacWilliams involution and the `nY`-parity involution generate
`S3` on the three linear forms

```text
x1=u+v+2w,  x2=u-v+2w,  x3=2u.
```

Their common degree-99 invariant space therefore has the monomial-symmetric
basis indexed by partitions of 99 into at most three parts. Its exact
dimension is 867, so the combined equality rank on the 2,550 even-`nY`
variables is 1,683.

The coefficient `(nI,nY,nR)=(41,4,54)` is at least `n3`, but the merge
`nR=nX+nZ` loses the input size and allows unrelated codewords to collide in
that state. This makes it a potentially weak upper-bound target.

Two lightweight reduced-basis scouts were null:

- target maximization reached a 60-second HiGHS wall without a primal point;
- an interior-point feasibility run returned a solve error.

Neither status is evidence of infeasibility or an upper bound. No exact dual
certificate was obtained.

The next route is the fully refined four-variable state
`(nI,nX,nY,nZ)=(41,2,4,52)`, where `nX+nY=6` fixes the input size.

Reproduce the exact checkpoint:

```powershell
python -B attempts\wave139-gf4-n3-bound\derive_rank.py

python -B -m unittest discover `
  -s attempts\wave139-gf4-n3-bound -p "test_*.py" -v
```

No strict `n3` upper bound, code, graph, or Conway-99 resolution is claimed.
