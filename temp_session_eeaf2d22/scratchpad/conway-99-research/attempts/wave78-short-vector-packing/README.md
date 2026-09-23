# Wave 78: short-vector packing closure

Status: `DERIVED`; independent verification required.

Conditional on Waves 71 and 74, this package proves elementary set-packing
bounds on the outside neighborhoods of the forced integer `-4` eigenvectors.

The exact reductions are:

```text
norm 16 outside histograms:       4 -> 1
norm 18, h=0 outside histograms: 20 -> 7
norm 18, h=1 outside histograms:  6 -> 4
```

No surviving histogram is a graph construction. Norm 14 also remains live,
so the modular-theta count congruence is not contradicted. Conway-99 and
novelty remain `UNKNOWN`.

Replay:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave78-short-vector-packing\exact_check.py `
  --verify attempts\wave78-short-vector-packing\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave78-short-vector-packing -p "test_*.py" -v
```
