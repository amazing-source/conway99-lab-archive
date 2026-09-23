# Wave 151: binary triangle-root factor

Status: **exact partial construction; full factor UNKNOWN**.

Wave149 produced a prism-free 36-by-36 Gram matrix required of the binary
incidence block `C` around a root triangle. Wave151 attacks the first actual
integrality layer:

```text
C is binary 36x60,
each row has weight 10,
each column has two ones in each 12-row group,
C C^T equals the frozen Wave149 Gram matrix.
```

## Exact progress

Every 12-row group by itself is forced: its 60 columns are the 60 edges of
`K_12` after deleting a perfect matching. A factor for two groups is therefore
a permutation between two copies of this 60-edge set.

The stored permutation `Q1` gives an exact binary 24-by-60 factor:

- every row has weight 10;
- every column has two ones in both groups;
- both diagonal Gram blocks and the full `G_01` block replay exactly.

This is a genuine construction, but only for two of three groups.

## Unresolved third group

For the displayed `Q1`, an exact 1,620-Boolean Z3 model reports that no third
edge permutation realizes both `G_02` and `G_12`. No proof trace was exported,
so the status is auxiliary only. More importantly, it refutes at most this
one `Q1`; other exact first-stage factors remain possible.

The unrestricted three-group search reached exact squared residual 108 but
did not produce a certificate. Therefore the complete `C` problem remains
`UNKNOWN`, and the residual 60-vertex adjacency matrix `D` was not entered.

No solver-negative claim is promoted.

## Reproduce

```powershell
python attempts/wave151-triangle-root-factor/exact_check.py `
  --verify attempts/wave151-triangle-root-factor/exact-results.json

python -m unittest discover `
  -s attempts/wave151-triangle-root-factor -p "test_*.py" -v

.\.venv\Scripts\python.exe `
  attempts/wave151-triangle-root-factor/fixed_q1_q2_scout.py `
  --time-limit 120
```
