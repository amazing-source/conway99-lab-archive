# Wave 192: equality-face circuit elimination

This package analytically reconstructs and excludes the complete equality
face of the independently verified Wave191 theorem `Q>=6237`.

The two terminal branches are eliminated without search:

1. the all-type-one branch is incompatible with the second short affine
   axis word of a canonical checkerboard conic; and
2. every branch containing a selected type-three circuit has a nonprivate
   leaf word that forces a circuit outside the saturated equality pools.

The derived conditional conclusion is

```text
Q>=6238.
```

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave192-equality-face-proof-a\exact_check.py --verify attempts\wave192-equality-face-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave192-equality-face-proof-a\test_exact_check.py
```

The checker uses only fixed ternary vectors and symbolic equality formulas.
It does not search for a graph, code, cover, configuration, or isomorphism
class.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
