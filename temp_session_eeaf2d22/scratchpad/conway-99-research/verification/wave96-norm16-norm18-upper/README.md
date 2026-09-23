# Wave 96 clean-room verification

Verdict: **VERIFIED_WITH_CLARIFICATION**, conditional on the frozen
previously verified lattice, shell, modular, and scalar-theta inputs.

The independent checker confirms:

- `407*N16+43*N18 >= 2,165,002` at the prism-free rank-28 endpoint;
- a universal cap of 25 antipodal norm-16/norm-18 extensions per induced
  four-cycle would give the incompatible even upper bound `2,115,382`;
- the fixed-cycle projector leaves a 40-dimensional residual sphere, and
  its norm-16 metric relaxation contains an 80-point cross-polytope with
  minimum squared distance `104/5 > 14`, so that relaxation cannot prove
  the cap;
- every norm-20 vector is, conditionally on the frozen energy-floor input,
  an integer `-4` eigenvector with ten `+1` and ten `-1` coordinates;
- its sign support has at most three same-sign edges and at least 15
  alternating induced four-cycles;
- the rank-30 scalar prefix forces one cycle into at least 25 antipodal
  extensions through norm 20, so a universal cap of 24 would exclude that
  row.

The clarification is local: in the mixed `m=2` profile, a positive unit
that misses the `-2` vertex already violates `mu=2`; only after rejecting
that subcase may adjacency to `-2` be described as forced. The submitted
conclusion is unchanged.

Neither cap is proved. No `N16` or `N18` upper bound, rank exclusion,
Conway-99 resolution, or novelty result follows. The marked Jacobi route
remains `UNKNOWN` because its exact coset transformation law and signed
coefficient control are not established.

Reproduce:

```powershell
python -B verification\wave96-norm16-norm18-upper\independent_check.py `
  --verify verification\wave96-norm16-norm18-upper\independent-results.json
python -B -m unittest discover `
  -s verification\wave96-norm16-norm18-upper -p "test_*.py" -v
```
