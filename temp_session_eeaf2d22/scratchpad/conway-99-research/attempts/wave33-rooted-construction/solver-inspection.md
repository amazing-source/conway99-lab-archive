# Solver inspection before discovery run

The repository virtual environment contains:

```text
python-sat 1.9.dev7
CaDiCaL 1.9.5 wrapper exposed as cadical195
SciPy 1.18.0 MILP wrapper over bundled HiGHS
```

Inspected implementation points before execution:

- `pysat.card.CardEnc.equals` constructs equality by combining independently
  encoded at-least and at-most constraints.
- `pysat.solvers.Cadical195` identifies the wrapped solver as CaDiCaL 1.9.5,
  rejects unsupported incremental/warm-start modes, and calls the compiled
  `pysolvers.cadical195_*` interface.
- `scipy.optimize.milp` validates integrality codes, bounds, and sparse linear
  constraints before passing them to its bundled HiGHS wrapper. The returned
  status is treated only as discovery metadata.

Frozen local implementation hashes:

```text
adabf7fedfe60b36cbc3c48075770e87e3cd6c5b5a013552009ce96f282a890e  .venv/Lib/site-packages/pysat/card.py
253654d8efabae650a0d136ad2f2e6d30b57206b1fb70846c714197468a28f7e  .venv/Lib/site-packages/pysat/solvers.py
1019bacdbb9400cc54fa89aa39294fefe1c63d5a67fdab35f473364529ec72dd  .venv/Lib/site-packages/pysolvers.cp313-win_amd64.pyd
803785ebcc365d1c04967a267650953da01ed285ee8be1c7a66a9fe3dbf75c3c  .venv/Lib/site-packages/scipy/optimize/_milp.py
92d47727b06333f871f57427a6d9800481e3e9feeabd59d31320ded8028c5357  .venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp313-win_amd64.pyd
df51a5cdf24f3ff1f06f36ef25c88b0ea41c496f8f7e12bfd40ca840f56d30a5  .venv/Lib/site-packages/scipy/optimize/_highspy/_highs_options.cp313-win_amd64.pyd
```

The solver is used only to discover a positive finite-relaxation witness.
Its exit status is not a certificate. Every accepted witness is rechecked
from its explicit edge list by `exact_check.py`, which uses only the Python
standard library. No solver nonhit or UNSAT response will be promoted.
