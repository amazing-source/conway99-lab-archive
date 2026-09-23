# Wave 198 orientation-lift proof B

The two orientations of a nonedge each have exact-three flag capacity
five.  Retaining this orientation information gives

```text
S5=5*3564-3*n3-4*p3-5*a3-5*b3>=0
```

and the conditional exact result `Q>=7037`.

Run:

```powershell
python -B attempts/wave198-orientation-lift-proof-b/exact_check.py --verify attempts/wave198-orientation-lift-proof-b/exact-results.json
python -B -m unittest -v attempts/wave198-orientation-lift-proof-b/test_exact_check.py
```

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
