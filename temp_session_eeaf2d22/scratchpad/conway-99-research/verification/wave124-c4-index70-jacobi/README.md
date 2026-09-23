# Wave 124 independent verification

Verdict: **VERIFIED_WITH_CLARIFICATIONS**.

The verifier froze all 12 discovery files before opening any Wave 124
source.  A clean-room reconstruction then confirmed the primitive C4
marking, indices 70 and 10, exact divisibility seven on the K side, the
q^7 through q^10 incidence interpretation, the Fricke/residue reduction,
and both tight-frame second moments.

After the clean-room result was sealed in `precomparison.sha256`, a second
independent implementation reconstructed the full-level Jacobi calculation
using only q^3.  It exactly reproduced all 18 holomorphic basis vectors, all
17 cusp basis vectors, and the five published A-power cusp directions from
the discovery package, which used q^10.

The result does **not** exclude rank 28 or rank 30.  The full-level
`J_{22,10}(SL_2(Z))` basis is only a controlled subspace of the whole
level-seven space, and the explicit oldform directions are signed.  No
positive graph-compatible unbounded ray or exact upper dual is present.
Conway-99 and novelty remain `UNKNOWN`.

One follow-up is recorded as `CANDIDATE`, not self-verified: once the
q^7 graph support zeros `|ell|>4` are imposed, vanishing of the five even
Taylor moments through degree eight kills the oldform target coefficient.
This identifies the degree-eight moment quotient as the first sharp model
to test.

Reproduce with:

```powershell
python verification/wave124-c4-index70-jacobi/independent_verify.py --verify --output verification/wave124-c4-index70-jacobi/independent-results.json
python verification/wave124-c4-index70-jacobi/independent_jacobi_audit.py --verify verification/wave124-c4-index70-jacobi/independent-jacobi-results.json
python verification/wave124-c4-index70-jacobi/compare_sealed.py
python -m unittest discover -s verification/wave124-c4-index70-jacobi -p "test_*.py" -v
```

See `verification-report.md` for the mathematical audit and
`comparison.json` for machine-readable agreement.
