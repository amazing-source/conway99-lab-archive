# Wave 78 clean-room verification

Status: **VERIFIED, conditional on the Wave 71 signed-unit support reduction
and the Wave 74 verified support-incidence equations**.

This package independently proves the short-vector set-packing bounds,
audits the rigid equality case on nine points, proves the norm-18 \(h=1\)
degree-three endpoint exclusion, and reproduces the exact 1/7/4 histogram
collapse without importing discovery Python code.

The verification does not construct a labelled incidence system or graph.
It does not exclude norm 14 or all short-vector alternatives. Conway-99 and
novelty remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe verification\wave78-short-vector-packing\independent_check.py --verify --json
.\.venv\Scripts\python.exe -m unittest -v verification\wave78-short-vector-packing\test_independent_check.py
```
