# Wave 154: triangle-factor portfolio

Status: **two exact Q1 symmetry orbits; complete factor UNKNOWN**.

Wave154 replaces fixed-first-stage search by a joint three-dimensional exact
cover. A primary variable chooses one column triple `(e0,e1,e2)` from the 60
nonmatching edges in each 12-row group. Zero-capacity triples are removed
before solving.

The joint model has 69,270 primary triples, 180 edge-capacity rows, 432
cross-Gram rows, and 1,039,050 integer incidences. The explicit centralizer of
the Wave149 matching and shift has order 384 and splits the allowed triples
into 292 orbits.

## Exact progress

A second exact 24-by-60 factor was found. Its `Q1` lies outside every one of
the 384 conjugates of Wave151's `Q1`, so this is a genuinely distinct local
symmetry orbit rather than a relabeling.

Both displayed Q1 branches have negative fixed-Q1 Z3 statuses, but neither
has an exported checkable proof and the two branches do not exhaust all Q1
factors. They remain branch-scoped discovery results.

Joint native-cardinality SAT and joint MILP runs ended without candidates or
proofs. Therefore the complete 36-by-60 factor remains `UNKNOWN`, and the
residual `D` layer remains `NOT_REACHED`.

No solver-negative claim, prism claim, or improved bound is made.

## Reproduce

```powershell
python attempts/wave154-triangle-factor-portfolio/exact_check.py `
  --verify attempts/wave154-triangle-factor-portfolio/exact-results.json

python -m unittest discover `
  -s attempts/wave154-triangle-factor-portfolio -p "test_*.py" -v
```
