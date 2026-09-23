# Wave 2 clean-clone replay

Verdict: `PASS` for the committed Wave 2 package; target status `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-22T21:00:00Z
git_commit: 0c2c1966817fe4f213c1fd13c63574e541441bfe
claim_label: VERIFIED
scope: tests, validators, dependency installation, and native positive control
limitations: no target certificate or target UNSAT proof exists to replay
```

A no-hardlink clone of the committed branch was created in a new temporary
directory. A new virtual environment was created inside that clone and
`requirements-search.txt` installed `python-sat==1.9.dev7` from its CPython
3.13 Windows wheel.

The following checks passed without using the original worktree's virtual
environment:

```text
verification unit tests: 11/11 PASS
discovery/code unit tests: 24/24 PASS
Python rook-graph validator: PASS on both exact paths
PowerShell rook-graph validator: PASS
native MiniCard pair_count=2 control: SAT_MODEL
decoded control dimensions: 9 vertices, 18 edges
clean-clone Git status after checks: clean (the virtual environment is ignored)
```

Commands:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --requirement requirements-search.txt
python -m unittest discover -s verification -p "test_*.py" -v
.venv\Scripts\python -m unittest discover -s code -p "test_*.py" -v
python verification\check_srg.py verification\fixtures\rook-3x3.srg.json `
  --vertices 9 --degree 4 --lambda 1 --mu 2
powershell -NoProfile -ExecutionPolicy Bypass `
  -File verification\Check-Srg.ps1 `
  -Certificate verification\fixtures\rook-3x3.srg.json `
  -Vertices 9 -Degree 4 -AdjacentCommon 1 -NonadjacentCommon 2
.venv\Scripts\python code\sat_model.py --pair-count 2 `
  --cardinality native --solve
```

This replay verifies reproducibility of the current infrastructure and
recorded necessary-condition package. It cannot satisfy the decisive-artifact
obligation because neither a 99-vertex positive certificate nor a complete
target nonexistence proof has been produced.
