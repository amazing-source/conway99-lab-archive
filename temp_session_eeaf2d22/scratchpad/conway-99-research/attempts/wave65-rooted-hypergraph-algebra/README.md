# Wave 65: rooted hypergraph algebra

Status: **DERIVED exact null result; pending independent verification**.

At the prism-free endpoint, the 420 disjoint-label residual edges are the
point graph of a linear 3-uniform, 5-regular hypergraph with 84 points and
140 blocks. If `Z` is its incidence matrix, then

```text
D+5I = ZZ^T.
```

The block-intersection graph `R=Z^T Z-3I` is 12-regular, has local graph
`3K4`, has least eigenvalue at least `-3`, and has eigenvalue `-3` with
multiplicity at least 56. Exact fourth moments give

```text
c4(R)=1260+c4(D),
```

so any endpoint target requires `1260<=c4(R)<=2331`.

The package also derives the exact scalar mixed-moment restriction

```text
64/5 <= tr(T E_3) <= 16
```

and checks the scaffold-averaged PSD condition for every integer endpoint
parameter. Both routes remain feasible. An exact local positive control
shows that the hypergraph, transition-factor, and local-triangle conditions
can coexist, while explicitly failing the target residual moments.

The first missing layer is the noncommutative two-root placement of `Z` and
`T` relative to the fixed scaffold line graph `Q`. The endpoint and Conway-99
remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave65-rooted-hypergraph-algebra\exact_check.py `
  --verify attempts\wave65-rooted-hypergraph-algebra\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave65-rooted-hypergraph-algebra -p "test_*.py" -v
```

Only Python standard-library integer and rational arithmetic is used.
