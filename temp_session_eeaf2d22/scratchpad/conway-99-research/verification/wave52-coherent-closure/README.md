# Independent verification of Wave 52

Status: `VERIFIED` only for the stated one-root computation. The result is a
verified null result: it finds no coherent-closure obstruction, constructs no
Conway graph, and does not improve the general `n3 <= 4158` bound. The
prism-free endpoint and Conway-99 remain `UNKNOWN`.

The verifier was written independently and does not import
`attempts/wave52-coherent-closure/coherent_closure.py`. It freezes the complete
discovery package before comparison, rebuilds both finite colored structures
from typed nodes and semantic incidences, and runs its own exact ordered-pair
2-dimensional Weisfeiler-Leman refinement.

## Verified results

- One root triangle has 18 other incident triangles, partitioned into three
  six-petal sectors. Their `K` relation is exactly `3K6`.
- The prism-free global triangle-relation valencies in order
  `(I,K,D,C,B)` are `(1,18,32,144,36)`.
- For one petal and one opposite six-petal sector, the forced degrees are
  `B=2`, `C=4`, and `D=0`.
- The uncompleted 19-triangle coloring starts and remains at six 2-WL colors.
- The completion-free 163-node incidence object follows the exact trajectory
  `26 -> 38 -> 47`; its diagonal class sizes are `1,18,36,108`.
- All stable colors have constant exact integer intersection numbers.
- All 64 canonical triples of bipartite 2-factor cycle profiles satisfy every
  exact-two cap. They produce 39 independent closure fingerprints and stable
  color counts from 8 through 361.
- The independent and discovery computations agree on all 64 color counts,
  all 64 refinement depths, and all 4,096 pairwise fingerprint-equivalence
  decisions.
- Completed closures depend on selected `B` edges: the all-`(6)` example has
  13 stable colors, while the all-`(2,2,2)` example has 8.
- Five hostile mutations are rejected, including a weakened memory guard.

## Reproduce

```powershell
python -B verification\wave52-coherent-closure\independent_check.py `
  --verify verification\wave52-coherent-closure\independent-result.json

python -B -m unittest discover `
  -s verification\wave52-coherent-closure -p "test_*.py" -v
```

The verifier enforces at least 20 percent free physical memory. The 64
canonical completions diagnose cycle-profile dependence; they are not an
exhaustive enumeration of all jointly labelled local completions.
