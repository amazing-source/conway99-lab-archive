# Wave 195 fixed-center packet bound

This proof-B package reframes canonical exact-three flags at one graph
vertex as an intersecting family of 3-subsets of its seven triangle
blocks.  The resulting local theorem gives a new global capacity row:

```text
SG=3861-C+n1+2*n2-a3-b3>=0.
```

An exact nonnegative combination of `SG` with the verified Wave194 rows
proves, conditionally,

```text
Q>=6980.
```

Run:

```powershell
python -B attempts/wave195-packet-cohomology-proof-b/exact_check.py --verify attempts/wave195-packet-cohomology-proof-b/exact-results.json
python -B -m unittest -v attempts/wave195-packet-cohomology-proof-b/test_exact_check.py
```

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
