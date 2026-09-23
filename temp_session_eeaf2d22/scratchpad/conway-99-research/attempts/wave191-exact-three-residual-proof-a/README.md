# Wave 191: exact-three exclusion and joint residual amplification

This package records an analytic continuation of the independently verified
Wave190 residual-stability theorem.

The new local lemma excludes an exact-three raw circuit contained in a
type-three `3+6` leaf relation. The owner center contradicts proper-star
independence. The leaf center forces a canonical four-block support with
an all-equal coefficient word, contradicting the verified checkerboard
kernel.

Closing new residuals under exact-three companionship and coupling the
type-two and type-three uses of exact-one capacity gives the derived
conditional bound

```text
Q>=6237
```

for projective short circuits cross-realizing nonedges.

Run the small exact replay:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave191-exact-three-residual-proof-a\exact_check.py --verify attempts\wave191-exact-three-residual-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave191-exact-three-residual-proof-a\test_exact_check.py
```

The checker performs only fixed-vector arithmetic and coefficient
identities. It does not search for a graph, cover, code, configuration, or
isomorphism class.

Status: `DERIVED_INDEPENDENT_AUDIT_PASS_PENDING_SEALED_VERIFICATION`.
