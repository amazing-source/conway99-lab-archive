# Wave 189 orbit-closed star translations

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the verified prism-free rank-11 endpoint assumptions, private-label
star extractions are closed under the Wave 180 exact-three companion
involution.  The resulting exact coefficient certificate gives

```text
Q>=4851.
```

Equality would force a partition of all 4,158 nonedges by 1,386 selected
anticomplete triangle-stars and all 2,079 canonical checkerboard conics.
Subtracting a canonical conic relation from its containing `3+6` leaf
translate produces a new weight-seven cross relation, excluding equality:

```text
Q>=4852.
```

Including the 693 edge-isolated projective circuits gives the
circuit-specific scalar consequence

```text
B_4+...+B_9>=11090.
```

Wave 188's bound `18018` for all short dual words remains stronger
numerically.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave189-orbit-closed-star-translations\exact_check.py --verify attempts\wave189-orbit-closed-star-translations\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave189-orbit-closed-star-translations\test_exact_check.py
```
