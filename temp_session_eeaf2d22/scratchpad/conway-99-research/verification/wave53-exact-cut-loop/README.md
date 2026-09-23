# Wave 53 exact-cut-loop verification

Status: **REFUTED_IN_PART**.

The fixed 177-cut rational relaxation is independently and exactly feasible,
and the retained Wave49 cuts at roots `220`, `62`, and `221` are exact.
However, the discovery double-mirrors an already-full symmetric Wave45
coefficient stream.  The correct matrix census is 120 indefinite and 8 PSD,
not 128 indefinite, and all 12 displayed Wave45 direction quadratics are
wrong.

Authoritative files:

- `audit.md` — human audit and status boundary;
- `independent_check.py` / `independent-result.json` — preinspection
  clean-room exact replay;
- `preinspection-freeze.sha256` — separation ledger;
- `postinspection_comparison.py` / `comparison-result.json` — exact source
  comparison and root-cause reproduction;
- `test_independent_check.py` / `test-results.txt` — verifier tests;
- `run-report.yaml` — AGENTS.md run report;
- `package-manifest.sha256` — final package hashes.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B verification\wave53-exact-cut-loop\independent_check.py
.\.venv\Scripts\python.exe -B verification\wave53-exact-cut-loop\postinspection_comparison.py
.\.venv\Scripts\python.exe -B -m unittest verification\wave53-exact-cut-loop\test_independent_check.py -v
```

The discovery package was not edited.  Endpoint, strict-upper-bound,
integrality, graph, Conway-99, and novelty status remain `UNKNOWN`.
