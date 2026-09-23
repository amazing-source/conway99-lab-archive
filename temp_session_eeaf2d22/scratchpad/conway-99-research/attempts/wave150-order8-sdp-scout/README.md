# Wave 150: marked order-eight SDP and exact rank-one witness

Status: **CANDIDATE exact rational null witness; independent verification required**.

This package combines:

- the exact Wave 44 order-seven affine/rooted rows;
- all Wave 147 two-root order-eight coefficient matrices and ordinary
  deletion rows;
- all independently scoped Wave 148 marked degree/common-neighbor rows;
- nonnegative order-seven and order-eight counts; and
- both centered pair-root covariance matrices.

At the prism-free endpoint `n3=4158`, the numerical SDP lies on the Jensen
boundary.  For a root family with `R` ordered root embeddings and flag-count
vectors `c(theta)`, write

```text
s = sum_theta c(theta),
M = sum_theta c(theta)c(theta)^T.
```

Then every graph satisfies the stronger centered condition

```text
M - s*s^T/R >= 0.
```

The exact witness found here has equality in both root families:

```text
M_edge    = s_edge*s_edge^T/1386,
M_nonedge = s_nonedge*s_nonedge^T/8316.
```

## Exact result

The stored candidate has:

```text
order-seven support:          204 / 208
order-eight support:          874 / 916
h11:                          8316
exact equations replayed:   10,310
largest x8 denominator:           4
integer x8 coordinates:         865
```

The order-seven counts are exact integers.  Among the 874 positive
order-eight counts, 865 are integers, five have denominator two, and four
have denominator four.

This is a rational feasible point for the stated relaxation.  It is not a
graph and does not prove the Conway-99 target exists.

## Reconstruction

The floating HiGHS point is used only to choose the 874-coordinate support
and to round the order-seven counts.  Those rounded counts pass all 170 Wave
44 equations exactly.  Sparse elimination over `F_1000003` finds rank 874.
An 874-by-874 subsystem is then solved over `Q` with FLINT and replayed
against all 10,310 exact equations.

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave150-order8-sdp-scout\exact_rank1_witness.py `
  --select-only `
  --selection-output attempts\wave150-order8-sdp-scout\rank1-selection.json

.\.venv\Scripts\python.exe -B `
  attempts\wave150-order8-sdp-scout\exact_rank1_witness.py `
  --selection attempts\wave150-order8-sdp-scout\rank1-selection.json `
  --output attempts\wave150-order8-sdp-scout\exact-rank1-witness.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave150-order8-sdp-scout -p "test_*.py" -v
```

## Boundary

This exact witness retires the present two-root/order-eight relaxation as a
route to a stricter upper bound.  It does not survive or address arbitrary
higher-order overlap consistency.  The next useful lifts are:

1. triple-root flags whose products reach order eight or nine;
2. order-nine one-root/pair-root covariance;
3. the binary incidence factor and residual block compatibility isolated in
   Wave 149; or
4. a complete proof-producing full-domain construction/nonexistence search.

Until independent verification, the witness is `CANDIDATE`.  Even after
verification, the global interval remains `708 <= n3 <= 4158`.
