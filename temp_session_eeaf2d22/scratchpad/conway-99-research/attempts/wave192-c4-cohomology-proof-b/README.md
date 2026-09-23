# Wave 192 canonical-square cohomology package

This package freezes proof B's analytic exclusion of equality in the
conditional Wave191 circuit bound.

The result is

```text
Q>=6238
```

for projective short circuits cross-realizing graph nonedges, conditional
on the prism-free rank-11 endpoint and the frozen prior theorems.

The argument reconstructs the `Q=6237` equality geometry, pairs type-one
private labels by the canonical nonedge involution, uses both signed
star-axis translates of the checkerboard conic, and then treats the
type-three private and shared-label leaf words by ternary circuit
elimination.

Run:

```powershell
python -B attempts/wave192-c4-cohomology-proof-b/exact_check.py --verify attempts/wave192-c4-cohomology-proof-b/exact-results.json
python -B -m unittest -v attempts/wave192-c4-cohomology-proof-b/test_exact_check.py
```

Status: `DERIVED`, not independently verified.

