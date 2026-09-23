# Wave134 independent verification

Verdict: `VERIFIED` for the sealed, conditional algebraic checkpoint and its
explicit `UNKNOWN` boundary.

The verifier was derived independently from the frozen Wave2, Wave131, and
Wave132 statements. It does not import Wave134 discovery code. It checks the
sealed discovery manifest before consuming the two JSON result files.

The clean-room replay verifies:

- `C` has type `Z4^54 x Z2`, order `2^109`, while `Cperp` has type
  `Z4^44 x Z2`, order `2^89`;
- the primal torsion shadow is `R+<1>` and may contain weight seven, while
  the dual torsion code `D` has minimum weight at least eight;
- all 84 primal and 44 dual expanded forced compositions, representing
  8,557,760 and 4,126,784 distinct words respectively;
- `q_u+q_v` and `q_u-q_v` are distinct, with all four hostile edge/nonedge
  compositions reproduced exactly;
- the symmetrized MacWilliams substitution and normalization;
- 1,119 admissible primal transform orbits and, after the verifier's
  weight-92 correction, 1,114 admissible and 161 forbidden dual orbits; and
- invalidation of every stale preseal solve.

No rational or integral feasibility run exists for the corrected model. No
quaternary code, adjacency matrix, graph, or Conway-99 resolution was
constructed. Those outcomes remain `UNKNOWN`.

Reproduce:

```powershell
python -B verification\wave134-z4-symmetrized-enumerator\independent_verify.py `
  --verify verification\wave134-z4-symmetrized-enumerator\independent-results.json

python -B -m unittest discover `
  -s verification\wave134-z4-symmetrized-enumerator `
  -p "test_*.py" -v
```
