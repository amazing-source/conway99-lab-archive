# Wave 196: four-fiber Hilton--Milner rigidity

This package derives, conditionally on the prism-free rank-11 endpoint,

```text
Q>=7029.
```

The local nonneighbors of a center split into 21 two-star-block fibers of
size four. That fiber capacity sharpens the Hilton--Milner analysis:

- a nontrivial 13-member equality family has three block-pairs of degree
  five and therefore at least three forced leaf repetitions;
- a common-star family has at most twelve flags, since its `p`-neighbor
  determines the full leaf triangle.

Thus every center has at most 13 exact-three flags and at most 36 distinct
oriented exact-three leaf labels, so `F<=1287` and `J<=3564`. The new
global slack combines exactly with the verified Wave194 rows to give
`Q>=7029`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave196-four-fiber-hilton-milner-proof-a\exact_check.py --verify attempts\wave196-four-fiber-hilton-milner-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave196-four-fiber-hilton-milner-proof-a\test_exact_check.py
```

The checker evaluates only the two fixed Hilton--Milner equality templates
and exact arithmetic identities. It performs no graph, code, cover, SAT,
LP, configuration, enumeration, or isomorphism search.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
