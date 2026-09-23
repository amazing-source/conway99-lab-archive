# Wave 43 independent endpoint rank-28 verification

Verdict: **PASS**

Conditional on the prism-free endpoint,

```text
n3=4158  ==>  rank_F7(M)>=28.
```

This verifier independently reconstructs every endpoint edge type:

```text
2+2+2, 4+2, 3+3, 6.
```

It does not import either Wave 43 discovery checker. The even-type verifier
uses direct rank-pruned permutation backtracking instead of the discovery
subspace cover, batched exact Gaussian elimination instead of minor
scanning, and literal kernel-vector forms in its type-`6` CSP. Type `3+3`
receives a separate generic principal-pivot Schur-complement search.

## Exact result

| local type and mechanism | independently covered cases | survivors |
| --- | ---: | ---: |
| `222`, `rank(F)=4`, `rank(D)=0` | `332 * 10,395 = 3,451,140` | 0 |
| `24`, `rank(F)=3`, `rank(D)=0` | `1,352 * 10,395 = 14,054,040` | 0 |
| `6`, `rank(F)=1`, `rank(D)<=2` | `288 * 10,395 = 2,993,760` | 0 |
| `6`, `rank(F)=2`, `rank(D)=0` | 92,274 pivot/mate branches | 0 |
| `33`, `rank(D)=2` | 666,666 principal-pivot branches | 0 |

The direct derangement streams and all invariant branch counts agree with
discovery in 36/36 comparisons. Both zero-result CSPs accept separately
planted valid leaves in eleven nodes; matching-degree, matrix-rank, formula,
and target perturbations are rejected.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave43-rank28 -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave43-rank28\independent_check.py `
  --verify verification\wave43-rank28\independent-results.json `
  --deterministic

.\.venv\Scripts\python.exe -B `
  verification\wave43-rank28\comparison_check.py `
  --verify verification\wave43-rank28\comparison.json
```

The full replay is one foreground process. It periodically checks physical
memory and aborts before free memory falls below 15%.

## Scope wall

This is a conditional endpoint rank theorem. The global rank ceiling `44`
is compatible with rank `28`, so the endpoint is not excluded. It supplies
no strict general upper bound below `n3<=4158`, no graph, no Conway-99
resolution, and no novelty or priority conclusion.

