# Wave 190 residual-stability verifier

Status: `VERIFIED_WITH_SCOPE`.

This clean-room package verifies the conditional residual-stability theorem

```text
Q>=5544,
```

where `Q` counts projective short circuits cross-realizing nonedges in the
frozen prism-free rank-11 endpoint model.

The checker reconstructs exact-one slack, per-label raw/residual exclusion,
exact-three orbit capacity, the residual-slack decomposition, and the final
coefficient identity `6Q>=8C`. It imports and executes no discovery code.

The theorem is conditional. Its sharp row is an arithmetic pool assignment,
not a cover, code, graph, or endpoint. Rank 11, endpoint existence, novelty,
and Conway-99 remain unknown.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave190-residual-stability-verifier\independent_check.py --verify verification\wave190-residual-stability-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave190-residual-stability-verifier\test_independent_check.py
```
